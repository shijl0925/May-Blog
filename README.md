# May Blog


## Features
* User registration, forgot password, 
* Admin only pages including statistics and user management
* Database setup, including database migrations and CRUD examples
* Fast deployment on gunicorn and supervisor
* Powerful stack: back-end based on Python with Flask, front-end is Material Design for Bootstrap 4


## What's included?

* Blueprints
* flask-security for User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Mail for sending emails
* flask-admin(with AdminLTE3) for Admin management

## How to install

```
$ pip3 install -r requirements.txt
```

## How to run
```
$ python3 -m flask --help # for help

$ export FLASK_DEBUG=1
$ export FLASK_APP=app.main

$ python3 -m flask db init
$ python3 -m flask db migrate -m "Initial migration."
$ python3 -m flask db upgrade

$ python3 -m flask initdb
$ python3 -m flask run
```

## How to Migrate database
```
$ python3 -m flask db init # create the database or enable migrations
$ python3 -m flask db migrate # generate an initial migration
$ python3 -m flask db upgrade # apply the migration to the database
```

Running on http://127.0.0.1:5000/

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
