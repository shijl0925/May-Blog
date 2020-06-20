#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_security.script import CreateUserCommand, AddRoleCommand,\
    RemoveRoleCommand, ActivateUserCommand, DeactivateUserCommand
from app.controller.extensions import db
from app.model.models import Role, User
from app.controller.script import ResetDB, InitDB
from app import app

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

manager.add_command("reset_db", ResetDB())
manager.add_command("init_db", InitDB())

manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_role', AddRoleCommand())
manager.add_command('remove_role', RemoveRoleCommand())
manager.add_command('deactivate_user', DeactivateUserCommand())
manager.add_command('activate_user', ActivateUserCommand())


@manager.command
def runserver():
    def run():
        http_server = WSGIServer(('0.0.0.0', 8080), app)
        http_server.serve_forever()

    run()


if __name__ == '__main__':
    manager.run()
