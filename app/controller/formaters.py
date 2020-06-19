#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from pprint import pformat
from flask import Markup
from flask_wtf.csrf import generate_csrf


def _show_avatar(view, context, model, name):
    if not model.avatar_s:
        return ''

    return flask.Markup(
        '<img src="%s" style="height:36px;width:36px;">' % flask.url_for('auth.get_avatar', filename=model.avatar_s))


def _lock_user(view, context, model, name):
    if model.is_admin:
        return ""

    lock_user_url = flask.url_for(".lock_user_view")
    unlock_user_url = flask.url_for(".unlock_user_view")
    csrf_token = generate_csrf()
    if model.locked:
        _html = """
        <form action="{unlock_user_url}" method="POST">
            <input type="hidden" name="csrf_token" value="{csrf_token}"/>
            <input id="user_id" name="user_id"  type="hidden" value="{user_id}">
            <button type="submit" class="btn btn-block btn-outline-danger btn-flat btn-sm" style="width:90px;padding-left:2px;padding-right:2px;"><i class="fas fa-lock"></i> Locked</button>
        </form>
        """.format(unlock_user_url=unlock_user_url, user_id=model.id, csrf_token=csrf_token)
    else:
        _html = """
        <form action="{lock_user_url}" method="POST">
            <input type="hidden" name="csrf_token" value="{csrf_token}"/>
            <input id="user_id" name="user_id"  type="hidden" value="{user_id}">
            <button type="submit" class="btn btn-block btn-outline-success btn-flat btn-sm" style="width:90px;padding-left:2px;padding-right:2px;"><i class="fas fa-lock-open"></i> Unlocked</button>
        </form>
        """.format(lock_user_url=lock_user_url, user_id=model.id, csrf_token=csrf_token)

    return flask.Markup(_html)


def _send_mail(view, context, model, name):
    if model.confirmed_at:
        return "Confirmed"

    mail_url = flask.url_for(".send_mail_view")
    csrf_token = generate_csrf()

    _html = """
        <form action="{mail_url}" method="POST">
            <input type="hidden" name="csrf_token" value="{csrf_token}"/>
            <input id="user_id" name="user_id"  type="hidden" value="{user_id}">
            <button class="btn btn-block btn-outline-primary btn-flat btn-sm" style="width:90px;padding-left:2px;padding-right:2px;" type='submit'>Send Confirm</button>
        </form>
    """.format(
        mail_url=mail_url, user_id=model.id, csrf_token=csrf_token
    )

    return flask.Markup(_html)


def _show_roles(view, context, model, name):
    roles = model.get_role_names()
    _html = ""
    for role in roles:
        _html += """<h6>{role}</h6>""".format(role=role)
    return flask.Markup(_html)


def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = pformat(value, width=50)
    return Markup('<code style="width: 80%;">{}</code>'.format(json_value))


def line_formatter(view, context, model, name):
    value = getattr(model, name)
    if value:
        text = "".join([line for line in value.split("\n")])
        return Markup('<pre style="width:80%;">{}</pre>'.format(text))
    else:
        return None


def short_formatter(view, context, model, name):
    value = getattr(model, name)
    return str(value)[0:15]
