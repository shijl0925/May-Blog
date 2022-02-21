#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from app.model.models import User
from app.controller.extensions import jwt


class UserObject:
    def __init__(self, username, permissions):
        self.username = username
        self.permissions = permissions


# This function is called whenever a protected endpoint is accessed,
# and must return an object based on the tokens identity.
# This is called after the token is verified, so you can use
# get_jwt_claims() in here if desired. Note that this needs to
# return None if the user could not be loaded for any reason,
# such as not being found in the underlying data store
@jwt.user_loader_callback_loader
def my_user_loader_callback(identity):
    user = User.query.filter_by(username=identity).first()
    if not user:
        return None

    return UserObject(
        username=identity,
        permissions=user.has_permissions()
    )


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return flask.jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': r'{} token has expired!!!'.format(token_type)
    }), 401


def my_invalid_token_callback(reason):
    """If invalid token attempts to access a protected route."""
    message = "invalid token. reason: {}".format(reason)
    return flask.jsonify({"message": message}), 401


def my_unauthorized_token_callback(jwt_header):
    message = "unauthorized access"
    return flask.jsonify({"message": message}), 401
