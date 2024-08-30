#!/bin/bash

# set -e

mkdir -p /home/logs

export FLASK_DEBUG=1
export FLASK_APP=app.main

# Handles database migrations through Flask-Migrate
python3 -m flask db init
python3 -m flask db migrate -m "Initial migration."
python3 -m flask db upgrade

python3 -m flask initdb

/usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf
