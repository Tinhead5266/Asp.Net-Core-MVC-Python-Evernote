# -*- coding: utf-8 -*-
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailHelper:
    def __init__(self):
        cfg = "./config.ini"
        config_raw = configparser.RawConfigParser()
        config_raw.read(cfg)

        self.host = config_raw.get('EmailSection', 'host').encode('utf-8')
        self.port = config_raw.get('EmailSection', 'port').encode('utf-8')
        self.username = config_raw.get('EmailSection', 'username').encode('utf-8')
        self.password = config_raw.get('EmailSection', 'password').encode('utf-8')
        self.sender = config_raw.get('EmailSection', 'sender').encode('utf-8')
        self.receiver = config_raw.get('EmailSection', 'receiver').encode('utf-8')

        self.smtp = smtplib.SMTP()
        self.smtp.connect(self.host, self.port)
        self.smtp.login(self.username, self.password)
        pass

    def SendEmail(self, message_info):
        subject = '自动更新笔记报告'
        msg = MIMEMultipart('AutoUploadEvernoteNoteReport')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = self.receiver

        message_info = MIMEText(message_info, 'plain', 'utf-8')
        msg.attach(message_info)
        self.smtp.sendmail(self.sender, self.receiver, msg.as_string())
        self.smtp.quit()
