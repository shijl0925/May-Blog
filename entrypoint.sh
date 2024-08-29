#!/bin/bash

set -e

mkdir -p /home/logs

export FLASK_DEBUG=1
export FLASK_APP=app.main
python3 -m flask initdb

/usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf
