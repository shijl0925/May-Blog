#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_restful import reqparse

post_get_parser = reqparse.RequestParser()
post_get_parser.add_argument('page', type=int, location=['args', 'headers'], required=False)

setting_post_parser = reqparse.RequestParser()
setting_post_parser.add_argument('name', type=str, required=True, help="name is required", location=('json', 'values'))
setting_post_parser.add_argument('value', type=str, required=True, help="name is required", location=('json', 'values'))

setting_put_parser = reqparse.RequestParser()
setting_put_parser.add_argument('value', type=str, location=('json', 'values'))