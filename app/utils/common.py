#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import uuid
import flask
from urllib.parse import urlparse, urljoin
from app.config import BaseConfig


def strip_trailing_slash(url):
    while url.endswith('/'):
        url = url[:-1]
    return url


def redirect_back(default='posts.posts', **kwargs):
    for target in flask.request.args.get('next'), flask.request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return flask.redirect(target)
    return flask.redirect(flask.url_for(default, **kwargs))


def is_safe_url(target):
    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def remove_preview_avatar(filename):
    avatar_path = os.path.join(BaseConfig.AVATARS_SAVE_PATH, filename)
    if os.path.exists(avatar_path):
        os.remove(avatar_path)
