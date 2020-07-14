#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_restful import fields

category_fields = {
    'id': fields.Integer(),
    'name': fields.String(),
}

collection_fields = {
    'id': fields.Integer(),
    'name': fields.String(),
}

tag_fields = {
    'id': fields.Integer(),
    'name': fields.String(),
}

archive_fields = {
    'id': fields.Integer(),
    'label': fields.String(),
}

post_fields = {
    'id': fields.Integer(),
    'title': fields.String(),
    'content': fields.String(),
    'body': fields.String(),
    'slug': fields.String(),
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'background': fields.String(),
    'is_draft': fields.Boolean(),
    'is_privacy': fields.Boolean(),
    'is_markdown': fields.Boolean(),
    'deny_comment': fields.Boolean(),
    'category': fields.Nested(category_fields),
    'collection': fields.Nested(collection_fields),
    'tags': fields.List(fields.Nested(tag_fields)),
    'archive': fields.Nested(archive_fields)
}

setting_fields = {
    'id': fields.Integer(),
    'name': fields.String(),
    'value': fields.String()
}
