#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import flask
from werkzeug.local import LocalProxy
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity
)
from app.config import BaseConfig
from app.model.models import User
from app.controller.extensions import csrf

_datastore = LocalProxy(lambda: flask.current_app.extensions['security'].datastore)

auth_bp = flask.Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    if not os.path.exists(os.path.join(BaseConfig.AVATARS_SAVE_PATH, filename)):
        return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, 'default_avatar.png')
    return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, filename)


@csrf.exempt
@auth_bp.route('/obtain/token', methods=['POST'])
def api():
    """
    obtain account token:
    curl -H "Content-Type: application/json" -X POST -d "{\"username\":\"xxx\",\"password\":\"xxx\"}" http://localhost:8080/auth/obtain/token
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
    return flask.jsonify(ret), 201


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@csrf.exempt
@auth_bp.route('/refresh/access/token', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    curl -X POST http://localhost:8080/auth/refresh/access/token -H "Authorization: Bearer $access_token"
    :return:
    """
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return flask.jsonify(ret), 201


@auth_bp.route('/me', methods=["GET"])
@jwt_required
def about_me():
    """
    curl -X GET http://localhost:8080/auth/me -H "Authorization: Bearer $access_token"
    """
    identity = get_jwt_identity()
    search_user = User.query.filter_by(username=identity).first()
    if search_user is None:
        return {"message": "unknown user"}, 400

    ret = search_user.to_dict()
    return ret
