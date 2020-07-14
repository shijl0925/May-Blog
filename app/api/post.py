#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required
from app.model.models import Post
from app.controller.extensions import db
from app.utils.decorator import jwt_permission_required
from app.api.parsers import post_get_parser
from app.api.fields import post_fields


class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self, slug=None):
        if slug:
            post = Post.query.filter_by(slug=slug).first()
            if not post:
                flask.abort(404)
            return post
        else:
            args = post_get_parser.parse_args()
            page = args.get('page', 1)
            pagination = Post.query.filter_by(is_draft=False).paginate(page=page, per_page=5)
            return pagination.items
