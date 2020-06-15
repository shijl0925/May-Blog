#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
from datetime import datetime
from flask_avatars import Identicon
from flask import current_app
from werkzeug.local import LocalProxy
from flask_security import UserMixin, RoleMixin
from flask_security.utils import verify_password, encrypt_password
from app.controller.extensions import db
from app.config import BaseConfig


_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


# relationship table
roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')

    def __repr__(self):
        return '<Permission %r>' % self.name


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32), unique=True)

    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')

    users = db.relationship('User', secondary=roles_users, back_populates='roles')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def init_role():
        roles_permissions_map = {
            'Locked': ['FOLLOW', 'COLLECT'],
            'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST'],
            'Moderator': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST', 'MODERATE'],
            'Administrator': ['FOLLOW', 'COLLECT', 'COMMENT', 'POST', 'MODERATE', 'ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = _datastore.find_or_create_role(name=role_name)
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(256))
    active = db.Column(db.Boolean())
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    username = db.Column(db.String(64), unique=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(256), nullable=True)
    location = db.Column(db.String(64), nullable=True)

    confirmed_at = db.Column(db.DateTime())

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(128))
    current_login_ip = db.Column(db.String(128))
    login_count = db.Column(db.Integer)

    locked = db.Column(db.Boolean, default=False)

    roles = db.relationship('Role', secondary=roles_users, back_populates='users')

    posts = db.relationship('Post', back_populates='author')

    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_role()
        self.generate_avatar()

    def set_role(self):
        if len(self.roles) == 0:
            if User.query.first() is None:
                self.roles.append(Role.query.filter_by(name='Administrator').first())
            else:
                self.roles.append(Role.query.filter_by(name='User').first())
            db.session.commit()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    def validate_password(self, password):
        return verify_password(password, self.password)

    def set_password(self, password):
        self.password = encrypt_password(password)

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if not user:
            return None

        # Do the passwords match
        if not verify_password(password, user.password):
            return None

        return user

    def lock(self):
        self.locked = True
        locked_role = Role.query.filter_by(name='Locked').first()
        self.roles = [locked_role]
        db.session.commit()

    def unlock(self):
        self.locked = False
        user_role = Role.query.filter_by(name='User').first()
        self.roles = [user_role]
        db.session.commit()

    @property
    def is_admin(self):
        return self.has_role('Administrator')

    def get_role_names(self):
        roles = [item.name for item in self.roles]
        return roles

    def get_permission_names(self):
        permissions = []
        for role in self.roles:
            permissions.extend(role.permissions)

        return [item.name for item in list(set(permissions))]

    def can(self, permission_name):
        return permission_name in self.get_permission_names()

    @property
    def full_name(self):
        return self.last_name + ' ' + self.first_name


@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    target = kwargs['target']
    for filename in [target.avatar_s, target.avatar_m, target.avatar_l, target.avatar_raw]:
        if filename is not None:  # avatar_raw may be None
            path = os.path.join(BaseConfig.AVATARS_SAVE_PATH, filename)
            if os.path.exists(path):  # not every filename map a unique file
                os.remove(path)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', back_populates='category')

    def __repr__(self):
        return '<Category %r>' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(256), nullable=False)
    body = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(256), nullable=False)

    is_draft = db.Column(db.Boolean, default=False)

    create_time = db.Column(db.DateTime, default=datetime.now)
    publish_time = db.Column(db.DateTime)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='posts')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')

    def __repr__(self):
        return '<Post %r>' % self.slug


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), unique=True)
    value = db.Column(db.String(128), nullable=True)
