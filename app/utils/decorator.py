#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from functools import wraps
from flask_security import current_user
from flask import current_app
from werkzeug.local import LocalProxy
from flask_security.decorators import _get_unauthorized_view
from flask_jwt_extended import current_user as jwt_current_user


_security = LocalProxy(lambda: current_app.extensions['security'])


def permission_required(permission):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.can(permission):
                if _security._unauthorized_callback:
                    return _security._unauthorized_callback()
                else:
                    return _get_unauthorized_view()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


def jwt_permission_required(permission):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            current_permissions = jwt_current_user.permissions
            if permission not in current_permissions:
                flask.abort(403)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
