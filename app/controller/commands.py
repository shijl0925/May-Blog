#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import sys
import click
import uuid
import subprocess
from datetime import datetime
from flask.cli import with_appcontext

from app.controller.extensions import db

from app.model.models import (
    Role,
    Category,
    Tag,
)


@click.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
@with_appcontext
def initdb(drop):
    """Initialize the database."""
    if drop:
        click.confirm('This operation will delete the database, do you want to continue?', abort=True)
        db.drop_all()
        click.echo('Drop tables.')

    db.create_all()

    Role.init_role()
    Category.init_category()
    Tag.init_tag()

    click.echo('Initialized database.')
