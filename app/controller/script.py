#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import random
from faker import Faker
from slugify import slugify
from flask_script import Command
from app.controller.extensions import db
from app.model.models import User, Role, Category, Tag, Post, Comment, Collection


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


class FakerData(Command):
    """create some faker test data"""
    def run(self, **kwargs):
        admin = User.query.get(1)
        faker = Faker()
        category_names = [
                    '技术文章',
                    '思考总结',
                    '生活记录',
                    '读书电影'
                ]
        tag_names = [
            'Python',
            'Flask',
            'Django',
            'CI/CD',
            'Jenkins',
            'Docker',
            'K8S'
        ]

        backgrounds = [
            'http://localhost:8000/files/background_image_1.jpg',
            'http://localhost:8000/files/background_image_2.jpg',
            'http://localhost:8000/files/background_image_3.jpg',
            'http://localhost:8000/files/background_image_4.jpg',
            'http://localhost:8000/files/background_image_5.jpg',
            'http://localhost:8000/files/background_image_6.jpg',
            'http://localhost:8000/files/background_image_7.jpg',
        ]

        for i in range(10):
            name = faker.text(max_nb_chars=50)
            description = faker.text(max_nb_chars=150)
            timestamp = faker.date_time_this_year()
            background = random.choice(backgrounds)

            topic = Collection(
                name=name,
                description=description,
                background=background,
                timestamp=timestamp
            )
            db.session.add(topic)
            db.session.commit()
            print("Create a Fake Topic {}".format(topic))

        for i in range(50):
            title = faker.text(max_nb_chars=50)
            slug = slugify(title, max_length=100)
            body = "<p>{}</p>".format(faker.text(max_nb_chars=2000))

            timestamp = faker.date_time_this_year()
            background = random.choice(backgrounds)

            post = Post(
                title=title,
                slug=slug,
                timestamp=timestamp,
                body=body,
                background=background,
                author=admin
            )
            db.session.add(post)
            db.session.commit()

            post.category = Category.query.filter_by(name=random.choice(category_names)).first()
            post.tags = [Tag.query.filter_by(name=item).first() for item in random.sample(tag_names, random.randint(1, 7))]
            post.visit_count = random.randint(1, 100)
            db.session.commit()

            for i in range(random.randint(1, 10)):
                comment = Comment(
                    author=faker.name(),
                    email=faker.email(),
                    timestamp=faker.date_time_this_year(),
                    body=faker.sentence()
                )
                db.session.add(comment)
                db.session.commit()

                post.comments.append(comment)
                db.session.commit()
            print("Create a Fake Post {}".format(title))

