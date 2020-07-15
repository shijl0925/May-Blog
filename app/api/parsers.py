#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_restful import reqparse

post_get_parser = reqparse.RequestParser()
post_get_parser.add_argument(
    'page',
    type=int,
    location=['args', 'headers'],
    required=False
)

post_post_parser = reqparse.RequestParser()
post_post_parser.add_argument(
    'title',
    type=str,
    required=True,
    help="Title is required",
    location=('json', 'values')
)
post_post_parser.add_argument(
    'content',
    type=str,
    required=True,
    help="Content is required",
    location=('json', 'values')
)
post_post_parser.add_argument(
    'background',
    type=str,
    required=True,
    help="Background is required",
    location=('json', 'values')
)
post_post_parser.add_argument(
    'is_draft',
    type=bool,
    location=('json', 'values')
)
post_post_parser.add_argument(
    'is_privacy',
    type=bool,
    location=('json', 'values')
)
post_post_parser.add_argument(
    'is_markdown',
    type=bool,
    location=('json', 'values')
)
post_post_parser.add_argument(
    'deny_comment',
    type=bool,
    location=('json', 'values')
)
post_post_parser.add_argument(
    'category',
    type=str,
    required=True,
    help="Category is required",
    location=('json', 'values')
)
post_post_parser.add_argument(
    'collection',
    type=str,
    location=('json', 'values')
)
post_post_parser.add_argument(
    'tags',
    type=str,
    required=True,
    action='append',
    location=('json', 'values')
)


post_put_parser = reqparse.RequestParser()
post_put_parser.add_argument(
    'title',
    type=str,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'content',
    type=str,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'background',
    type=str,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'is_draft',
    type=bool,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'is_privacy',
    type=bool,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'is_markdown',
    type=bool,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'deny_comment',
    type=bool,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'category',
    type=str,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'collection',
    type=str,
    location=('json', 'values')
)
post_put_parser.add_argument(
    'tags',
    type=str,
    action='append',
    location=('json', 'values')
)

setting_post_parser = reqparse.RequestParser()
setting_post_parser.add_argument(
    'name',
    type=str,
    required=True,
    help="name is required",
    location=('json', 'values')
)
setting_post_parser.add_argument(
    'value',
    type=str,
    required=True,
    help="name is required",
    location=('json', 'values')
)

setting_put_parser = reqparse.RequestParser()
setting_put_parser.add_argument(
    'value',
    type=str,
    location=('json', 'values')
)