#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import queue
import threading
import time
from queue import Queue
from typing import Optional


logger = logging.getLogger(__name__)


class AsyncWorker:
    def __init__(self, running_fnc=None):
        self.task_queue: Optional[asyncio.Queue] = None
        self.is_running = True
        self.is_running_fnc = running_fnc
        self.buffer = []

    def _check_is_running(self):
        if self.is_running_fnc and not self.is_running_fnc():
            return False
        return self.is_running

    async def work(self):
        """Starts work loop on task_queue. Remember to call stop() to terminate this coroutine."""
        self.is_running = True
        self.task_queue = asyncio.Queue()
        for x in self.buffer:
            self.task_queue.put_nowait(x)
        self.buffer = None

        while self._check_is_running():
            try:
                # next_task = self.task_queue.get_nowait()
                next_task = await self.task_queue.get()

                if not next_task:
                    continue

                await next_task
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.05)

    def enqueue(self, task):
        """Enqueues coroutine function for execution"""
        if not self.task_queue:
            self.buffer.append(task)
            return

        self.task_queue.put_nowait(task)

    def stop(self):
        self.task_queue.put_nowait(None)  # unblocks waiting
        self.is_running = False


class Worker:
    def __init__(self, running_fnc=None):
        self.worker_thread = None
        self.worker_queue = Queue()
        self.is_running = True
        self.is_running_fnc = running_fnc

    def _check_is_running(self):
        if self.is_running_fnc and not self.is_running_fnc():
            return False
        return self.is_running

    def start_worker_thread(self, queue_timeout=0.5):
        self.is_running = True

        def worker_internal():
            logger.info(f'Starting worker thread')
            while self._check_is_running():
                try:
                    next_task = self.worker_queue.get(True, queue_timeout)
                    if not next_task:
                        continue

                    try:
                        next_task()
                    except Exception as e:
                        logger.error(f'Top-level error at worker thread {e}', exc_info=e)
                except queue.Empty:
                    time.sleep(0.02)
            logger.info(f'Stopping worker thread')

        self.worker_thread = threading.Thread(target=worker_internal, args=())
        self.worker_thread.daemon = False
        self.worker_thread.start()

    def enqueue(self, task):
        """Enqueues lambda function for execution"""
        self.worker_queue.put(task)

    def stop(self):
        self.is_running = False

