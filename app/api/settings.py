#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required
from app.model.models import Settings
from app.controller.extensions import db
from app.utils.decorator import jwt_permission_required
from app.api.parsers import setting_post_parser, setting_put_parser
from app.api.fields import setting_fields


class SettingsApi(Resource):
    """
    curl -X GET -H "Authorization: Bearer $access_token" http://localhost:8000/api/settings
    curl -X POST -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" -d "{\"name\":\"xxx\",\"value\":\"xxx\"}" http://localhost:8000/api/settings
    curl -X PUT -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" -d "{\"value\":\"xxx\"}" http://localhost:8000/api/settings/xxx
    curl -X DELETE -H "Authorization: Bearer $access_token" http://localhost:8000/api/settings/xxx
    """
    @jwt_required
    @jwt_permission_required("ADMINISTER")
    @marshal_with(setting_fields)
    def get(self, name=None):
        if name:
            setting = Settings.query.filter_by(name=name).first()
            if not setting:
                flask.abort(404)
            return setting
        else:
            settings = Settings.query.all()
            return settings

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def post(self):
        args = setting_post_parser.parse_args(strict=True)
        setting_name = args.get('name')
        setting_value = args.get('value')

        search_setting = Settings.query.filter_by(name=setting_name).first()
        if search_setting:
            return "already exists.", 400

        new_settings = Settings(name=setting_name, value=setting_value)
        db.session.add(new_settings)
        db.session.commit()
        return {'id': new_settings.id}, 201

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def put(self, name=None):
        if not name:
            flask.abort(400)
        setting = Settings.query.filter_by(name=name).first()
        if not setting:
            flask.abort(404)

        args = setting_put_parser.parse_args(strict=True)
        setting_value = args.get('value')
        if setting_value:
            setting.value = setting_value
            db.session.commit()

        return {'id': setting.id}, 201

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def delete(self, name=None):
        if not name:
            flask.abort(400)
        setting = Settings.query.filter_by(name=name).first()
        if not setting:
            flask.abort(404)

        db.session.delete(setting)
        db.session.commit()
        return "", 204
