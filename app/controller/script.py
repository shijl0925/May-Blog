#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_script import Command
from app.controller.extensions import db
from app.model.models import Role, Category, Tag


class ResetDB(Command):
    """Drops all tables and recreates them"""
    def run(self, **kwargs):
        db.drop_all()
        db.create_all()
        print('OK: database is reseted.')


class InitDB(Command):
    """Fills in predefined data to DB"""
    def run(self, **kwargs):
        db.create_all()
        Role.init_role()
        Category.init_category()
        Tag.init_tag()
        print('OK: database is initialed.')
