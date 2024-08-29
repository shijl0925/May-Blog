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
@with_appcontext
def initdb():
    """Initialize the database."""

    Role.init_role()
    Category.init_category()
    Tag.init_tag()

    click.echo('Initialized database.')
