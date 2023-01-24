#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from ph4monitlib.lib import try_fnc

logger = logging.getLogger(__name__)


class NotifyEmail:
    def __init__(self, server=None, user=None, passwd=None, port=587, timeout=20.0):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.port = port
        self.timeout = timeout

    def send_notify_email(self, recipients: List[str], txt_message: str, subject: str):
        if not self.server or not self.user or not self.passwd:
            return

        server = None
        context = ssl.create_default_context()

        try:
            logger.info(f'Sending email notification via {self.user}, msg: {txt_message[:80]}...')
            server = smtplib.SMTP(self.server, self.port, timeout=self.timeout)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self.user, self.passwd)

            for recipient in recipients:
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = self.user
                message["To"] = recipient
                part1 = MIMEText(txt_message, "plain")
                message.attach(part1)
                server.sendmail(self.user, recipient, message.as_string())
            return True

        except Exception as e:
            logger.warning(f'Exception when sending email {e}', exc_info=e)
            return e

        finally:
            try_fnc(lambda: server.quit())
