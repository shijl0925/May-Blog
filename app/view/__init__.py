#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from app.view.post import posts_bp
from app.view.auth import auth_bp
from app.view.file import file_bp

bps = [posts_bp, auth_bp, file_bp]


def init_blue_print(app):
    for bp in bps:
        app.register_blueprint(bp)
