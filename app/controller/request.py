#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from app.model.models import Request
from app.controller.extensions import db


def save_request(resp):
    if flask.request.method == "GET":
        args = flask.request.args.to_dict()
    else:
        args = flask.request.json

    nginx_remote = "X-Forwarded-For"
    ip = (
        flask.request.headers[nginx_remote]
        if nginx_remote in flask.request.headers
        else flask.request.remote_addr
    )

    module = flask.request.endpoint
    method = flask.request.method
    url = flask.request.path
    user_agent = flask.request.headers.get('User-Agent')

    request = Request(
        method=method,
        module=module,
        url=url,
        ip=ip,
        user_agent=user_agent,
        arguments=args,
        status_code=resp.status_code
    )
    db.session.add(request)
    db.session.commit()
    return resp

