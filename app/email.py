#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from threading import Thread
from flask_mail import Message
from app.controller.extensions import mail


def __send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject=subject, recipients=recipient, sender=flask.current_app.config['MAIL_DEFAULT_SENDER'])
    msg.html = flask.render_template(template+'.html', **kwargs)
    msg.body = flask.render_template(template+'.txt', **kwargs)
    mail.send(message=msg)


def send_async_email(to, subject, body, html):
    app = flask.current_app._get_current_object()
    msg = Message(subject, sender=flask.current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = body
    msg.html = html
    thr = Thread(target=__send_async_email, args=[app, msg])
    thr.start()
    return thr
