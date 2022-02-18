#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import flask
from werkzeug.local import LocalProxy
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity
from app.config import BaseConfig
from app.model.models import User
from app.controller.extensions import jwt, csrf

_datastore = LocalProxy(lambda: flask.current_app.extensions['security'].datastore)

auth_bp = flask.Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/settings/avatars/<path:filename>')
def get_avatar(filename):
    if not os.path.exists(os.path.join(BaseConfig.AVATARS_SAVE_PATH, filename)):
        return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, 'default_avatar.png')
    return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, filename)


@csrf.exempt
@auth_bp.route('/api/login', methods=['POST'])
def api():
    """
    generate account token:
    curl -H "Content-Type: application/json" -X POST -d "{\"username\":\"xxx\",\"password\":\"xxx\"}" http://localhost:8000/auth/api/login
    :return:
    """
    if not flask.request.is_json:
        return flask.jsonify({"msg": "Missing JSON in request"}), 400

    username = flask.request.json.get('username', None)
    password = flask.request.json.get('password', None)

    if not username:
        return flask.jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return flask.jsonify({"msg": "Missing password parameter"}), 400

    user = User.authenticate(username, password)
    if not user:
        return flask.jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    ret = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    return flask.jsonify(ret), 200


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@auth_bp.route('/api/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return flask.jsonify(ret), 200


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
def user_loader_callback(identity):
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

