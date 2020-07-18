#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from flask_restful import Api
from app.controller.extensions import csrf
from app.api.settings import SettingsApi
from app.api.post import PostApi

api_bp = flask.Blueprint('api', __name__, url_prefix='/api')
rest_api = Api(api_bp)
csrf.exempt(api_bp)

rest_api.add_resource(
    SettingsApi,
    '/settings',
    '/settings/<name>'
)

rest_api.add_resource(
    PostApi,
    '/posts',
    '/posts/<slug>'
)
