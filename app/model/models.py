#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict
from slugify import slugify
from flask_avatars import Identicon
from flask import current_app
from werkzeug.local import LocalProxy
from flask_security import UserMixin, RoleMixin
from flask_security.utils import verify_password, encrypt_password
from app.controller.extensions import db, whooshee
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

    nick_name = db.Column(db.String(64), nullable=True)
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
        return self.last_name + self.first_name


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

    @staticmethod
    def init_category():
        categories = [
            '技术文章',
            '思考总结',
            '生活记录',
            '读书电影'
        ]
        for item in categories:
            search_category = Category.query.filter_by(name=item).first()
            if search_category is None:
                category = Category(name=item)
                db.session.add(category)
        db.session.commit()

    def __repr__(self):
        return '<Category %r>' % self.name


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), unique=True)
    posts = db.relationship('Post', back_populates='collection')

    def __repr__(self):
        return '<Collection %r>' % self.name


post_tag = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(30), unique=True)
    posts = db.relationship('Post', secondary=post_tag, back_populates='tags')

    @staticmethod
    def init_tag():
        tags = [
            'Python',
            'Flask',
            'Django',
            'CI/CD',
            'Jenkins',
            'Docker',
            'K8S'
        ]
        for item in tags:
            search_tag = Tag.query.filter_by(name=item).first()
            if search_tag is None:
                tag = Tag(name=item)
                db.session.add(tag)
        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name


@whooshee.register_model('title', 'body')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    body = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime)
    background = db.Column(db.String(256), nullable=False)

    is_draft = db.Column(db.Boolean, default=False)
    is_privacy = db.Column(db.Boolean, default=False)
    is_markdown = db.Column(db.Boolean, default=False)
    deny_comment = db.Column(db.Boolean)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='posts')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')

    archive_id = db.Column(db.Integer, db.ForeignKey('archive.id'))
    archive = db.relationship('Archive', back_populates='posts')

    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    collection = db.relationship('Collection', back_populates='posts')

    tags = db.relationship('Tag', secondary='post_tag', back_populates='posts')

    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    trackers = db.relationship('Tracker', back_populates='post', cascade='all')
    visit_count = db.Column(db.Integer, default=0)

    @property
    def previous(self):
        return Post.query.order_by(Post.id.desc()).filter(Post.is_draft == False, Post.id < self.id).first()

    @property
    def next(self):
        return Post.query.order_by(Post.id.desc()).filter(Post.is_draft == False, Post.id > self.id).first()

    def __repr__(self):
        return '<Post %r>' % self.id

    __mapper_args__ = {"order_by": timestamp.desc()}


# @db.event.listens_for(Post, 'before_insert', named=True)
# @db.event.listens_for(Post, 'before_update', named=True)
# def render_post(**kwargs):
#     target = kwargs['target']
#     target.slug = slugify(target.title, max_length=100)
#     now = datetime.now()
#     target.timestamp = now


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    author = db.Column(db.String(30))
    email = db.Column(db.String(64))
    body = db.Column(db.Text)

    # reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    def __repr__(self):
        return '<Comment %r>' % self.id

    __mapper_args__ = {"order_by": timestamp.desc()}


@db.event.listens_for(Post.timestamp, 'set', named=True)
def update_post_archive(target, value, oldvalue, initiator):
    label = datetime.strftime(value, "%Y.%m")
    search_archive = Archive.query.filter_by(label=label).first()
    if search_archive is None:
        search_archive = Archive(label=label)

    target.archive = search_archive


class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    label = db.Column(db.String(32), nullable=False)
    posts = db.relationship('Post', back_populates='archive')

    def __repr__(self):
        return '<Archive %r>' % self.label

    __mapper_args__ = {"order_by": label.desc()}


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), unique=True)
    value = db.Column(db.String(128), nullable=True)


class Tracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    url = db.Column(db.String(128))
    ip = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_agent = db.Column(db.String(256))

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='trackers')

    def __repr__(self):
        return '<Tracker %r>' % self.id

    __mapper_args__ = {"order_by": timestamp.desc()}


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    method = db.Column(db.String(8))
    module = db.Column(db.String(32))

    url = db.Column(db.String(256))
    ip = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_agent = db.Column(db.String(256))

    status_code = db.Column(db.Integer)
    arguments = db.Column(MutableDict.as_mutable(db.PickleType), default=dict())

    def __repr__(self):
        return '<Request %r>' % self.id

    __mapper_args__ = {"order_by": timestamp.desc()}
