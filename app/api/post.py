#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import flask
from slugify import slugify
from datetime import datetime
from flask_restful import Resource, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model.models import User, Post, Tag, Category, Collection
from app.controller.extensions import db
from app.utils.decorator import jwt_permission_required
from app.api.parsers import post_get_parser, post_post_parser, post_put_parser
from app.api.fields import post_fields
from app.controller.md_ext import md


def add_tags_to_post(post, tags_list):
    for item in tags_list:
        tag = Tag.query.filter_by(name=item).first()
        if tag:
            post.tags.append(tag)
        else:
            new_tag = Tag(name=item)
            db.session.add(new_tag)
            db.session.commit()

            post.tags.append(new_tag)
            db.session.commit()


def add_category_to_post(post, category):
    search_category = Category.query.filter_by(name=category).first()
    if search_category:
        post.category = search_category
    else:
        new_category = Category(name=category)
        db.session.add(new_category)
        db.session.commit()

        post.category = new_category
        db.session.commit()


def add_collection_to_post(post, collection):
    search_collection = Collection.query.filter_by(name=collection).first()
    if search_collection:
        post.collection = search_collection
    else:
        new_collection = Collection(name=collection)
        db.session.add(new_collection)
        db.session.commit()

        post.collection = new_collection
        db.session.commit()


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
            page = args['page'] or 1
            pagination = Post.query.filter_by(is_draft=False).paginate(page=page, per_page=5)
            return pagination.items

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def post(self):
        args = post_post_parser.parse_args(strict=True)
        title = args['title']
        content = args['content']
        background = args['background']

        is_draft = args['is_draft'] or False
        is_privacy = args['is_privacy'] or False
        is_markdown = args['is_markdown'] or False
        deny_comment = args['deny_comment'] or False

        category = args['category']
        collection = args['collection'] or ""
        tags = args['tags']

        username = get_jwt_identity()

        if is_markdown:
            body = md.convert(content)
        else:
            body = content
        slug = slugify(title, max_length=100)

        search_post = Post.query.filter_by(slug=slug).first()
        if search_post:
            return "already exists.", 400

        new_post = Post(
            title=title,
            slug=slug,
            is_draft=is_draft,
            is_privacy=is_privacy,
            is_markdown=is_markdown,
            deny_comment=deny_comment,
            background=background,
            body=body,
            content=content,
            timestamp=datetime.now(),
        )
        db.session.add(new_post)

        add_category_to_post(new_post, category)
        add_collection_to_post(new_post, collection)
        add_tags_to_post(new_post, tags)

        author = User.query.filter_by(username=username).first()
        new_post.author = author

        db.session.commit()

        return {'id': new_post.id}, 201

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def put(self, slug=None):
        if not slug:
            flask.abort(400)
        post = Post.query.filter_by(slug=slug).first()
        if not post:
            flask.abort(404)

        args = post_put_parser.parse_args(strict=True)
        title = args['title']
        content = args['content']
        background = args['background']

        is_draft = args['is_draft']
        is_privacy = args['is_privacy']
        is_markdown = args['is_markdown'] or False
        deny_comment = args['deny_comment']

        category = args['category']
        collection = args['collection'] or ""
        tags = args['tags']

        if title:
            post.title = title
            slug = slugify(title, max_length=100)
            post.slug = slug

        if content:
            if is_markdown:
                body = md.convert(content)
            else:
                body = content

            post.content = content
            post.body = body

        if background:
            post.background = background

        if is_draft is not None:
            post.is_draft = is_draft

        if is_privacy is not None:
            post.is_privacy = is_privacy

        if deny_comment is not None:
            post.deny_comment = deny_comment

        if category:
            add_category_to_post(post, category)

        if collection:
            add_collection_to_post(post, collection)

        if tags:
            post.tags = []
            add_tags_to_post(post, tags)

        db.session.commit()

        return {'id': post.id}, 201

    @jwt_required
    @jwt_permission_required("ADMINISTER")
    def delete(self, slug=None):
        if not slug:
            flask.abort(400)
        post = Post.query.filter_by(slug=slug).first()
        if not post:
            flask.abort(404)

        db.session.delete(post)
        db.session.commit()
        return "", 204

