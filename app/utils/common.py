#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import uuid
import flask
import PIL
from PIL import Image
from urllib.parse import urlparse, urljoin


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
    avatar_path = os.path.join(flask.current_app.config['AVATARS_SAVE_PATH'], filename)
    if os.path.exists(avatar_path):
        os.remove(avatar_path)


def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += flask.current_app.config['FILEUPLOAD_IMG_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], filename), optimize=True, quality=85)
    return filename


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flask.flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

