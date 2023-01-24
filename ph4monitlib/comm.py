#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import select
import socket
import socketserver
import threading
import time

from ph4monitlib.lib import try_fnc

logger = logging.getLogger(__name__)


class FiFoComm:
    def __init__(self, fifo_path=None, handler=None, running_fnc=None):
        self.is_running = True
        self.is_running_fnc = running_fnc
        self.fifo_path = fifo_path
        self.fifo_thread = None
        self.handler = handler
        self.start_error = None
        self.start_finished = False

    def _check_is_running(self):
        if self.is_running_fnc and not self.is_running_fnc():
            return False
        return self.is_running

    def create_fifo(self):
        if not self.fifo_path:
            return
        os.mkfifo(self.fifo_path)

    def destroy_fifo(self):
        if not self.fifo_path:
            return
        try:
            if os.path.exists(self.fifo_path):
                os.unlink(self.fifo_path)
        except Exception as e:
            logger.warning(f'Error unlinking fifo {e}', exc_info=e)

    def start(self):
        self.start_finished = False
        if not self.handler:
            logger.warning(f'FiFo comm has no handler set')

        def fifo_internal():
            logger.info('Starting fifo thread')
            try:
                self.destroy_fifo()
                self.create_fifo()
                with open(self.fifo_path) as _:
                    pass

            except Exception as e:
                logger.error(f'Error starting server fifo: {e}', exc_info=e)
                self.start_error = e
                return
            finally:
                self.start_finished = True

            with open(self.fifo_path) as fifo:
                while self._check_is_running():
                    try:
                        select.select([fifo], [], [fifo])
                        data = fifo.read()
                        if not data:
                            continue

                        if self.handler:
                            self.handler(data)
                        else:
                            logger.warning(f'FiFo comm has no handler set')

                    except Exception as e:
                        logger.error(f'Fifo thread exception: {e}', exc_info=e)
                        time.sleep(0.1)
            logger.info('Stopping fifo thread')

        self.fifo_thread = threading.Thread(target=fifo_internal, args=())
        self.fifo_thread.daemon = False
        self.fifo_thread.start()

        ttime = time.time()
        while not self.start_finished:
            if self.start_error:
                raise self.start_error
            if time.time() - ttime > 30.0:
                raise ValueError('Init error: timeout')
            time.sleep(0.01)

    def stop(self):
        self.is_running = False
        try_fnc(lambda: self.destroy_fifo())

    def send_message(self, payload):
        """Send message to the fifo, as a client"""
        with open(self.fifo_path, 'w') as f:
            f.write(payload + '\n')
            f.flush()


class TcpComm:
    def __init__(self, host='127.0.0.1', port=9333, handler=None, running_fnc=None):
        self.is_running = True
        self.is_running_fnc = running_fnc

        self.server_host = host
        self.server_port = port
        self.handler = handler

        self.server_thread = None
        self.server_tcp = None
        self.start_error = None
        self.start_finished = False

    def _check_is_running(self):
        if self.is_running_fnc and not self.is_running_fnc():
            return False
        return self.is_running

    def start(self):
        if not self.handler:
            logger.warning(f'TcpComm has no handler set')

        sself = self
        self.start_finished = False

        class TcpServerHandler(socketserver.BaseRequestHandler):
            def handle(self):
                try:
                    data = self.request.recv(8192).strip()
                    if sself.handler:
                        r = sself.handler(data.decode())
                        self.request.sendall(r)
                    else:
                        logger.warning(f'TcpComm has no handler set')

                except Exception as e:
                    logger.warning(f'Exception processing server message {e}', exc_info=e)
                    self.request.sendall(json.dumps({'response': 500}).encode())

        def server_internal():
            logger.info('Starting server thread')
            try:
                self.server_tcp = socketserver.TCPServer((self.server_host, self.server_port), TcpServerHandler)
                self.server_tcp.allow_reuse_address = True

                self.start_finished = True
                self.server_tcp.serve_forever()
            except Exception as e:
                self.start_error = e
                logger.error(f'Error in starting server thread {e}', exc_info=e)
            finally:
                logger.info('Stopping server thread')

        self.server_thread = threading.Thread(target=server_internal, args=())
        self.server_thread.daemon = False
        self.server_thread.start()

        time.sleep(0.5)
        ttime = time.time()
        while not self.start_finished:
            if self.start_error:
                raise self.start_error
            if time.time() - ttime > 30.0:
                raise ValueError('Init error: timeout')
            time.sleep(0.01)

    def stop(self):
        if not self.server_tcp:
            return
        try:
            self.server_tcp.shutdown()
        except Exception as e:
            logger.error(f'Error in TCP server shutdown {e}', exc_info=e)

    def send_message(self, payload):
        """Send a message to the TCP server, as a client"""
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_client.connect((self.server_host, self.server_port))
            tcp_client.sendall((payload + '\n').encode())

            # Read data from the TCP server and close the connection
            received = tcp_client.recv(8192).decode()
            return received
        finally:
            tcp_client.close()
