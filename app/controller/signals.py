#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from datetime import datetime
import flask
from blinker import Namespace
from app.model.models import Tracker
from app.controller.extensions import db

blog_signals = Namespace()
post_visited = blog_signals.signal('post-visited')


@post_visited.connect
def on_post_visited(sender, post, **extra):
    nginx_remote = "X-Forwarded-For"
    ip = (flask.request.headers[nginx_remote] if nginx_remote in flask.request.headers else flask.request.remote_addr)

    search_tracker = Tracker.query.filter_by(ip=ip, post=post).first()

    if search_tracker is None:
        tracker = Tracker(
            url=flask.request.path,
            ip=ip,
            post=post
        )
        db.session.add(tracker)
        db.session.commit()

        post.visit_count += 1
        db.session.commit()
    else:
        search_tracker.timestamp = datetime.now()
        db.session.commit()
