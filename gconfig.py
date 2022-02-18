import gevent.monkey

gevent.monkey.patch_all()

import multiprocessing

# debug = True
bind = "0.0.0.0:8080"
pidfile = "app/logs/gunicorn.pid"
accesslog = "app/logs/gaccess.log"
errorlog = "app/logs/gdebug.log"
loglevel = 'info'
capture_output = True
# daemon = True

# 启动的进程数
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'

access_log_format = "%(h)s %(r)s %(s)s %(a)s %(L)s"

logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    "root": {
          "level": "DEBUG",
          "handlers": ["console"]
    },
    'loggers': {
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_file"],
            "propagate": 0,
            "qualname": "gunicorn.error"
        },
        "gunicorn.access": {
            "level": "DEBUG",
            "handlers": ["access_file"],
            "propagate": 0,
            "qualname": "gunicorn.access"
        },
        "gunicorn.api": {
            "level": "DEBUG",
            "handlers": ["api_file"],
            "propagate": 0,
            "qualname": "gunicorn.api"
        }
    },
    'handlers': {
        "error_file": {
            "class": "logging.FileHandler",
            "formatter": "generic",
            "filename": "app/logs/gerror.log"
        },
        "access_file": {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "maxBytes": 10*1024*1024,
            "backupCount": 5,
            "formatter": "generic",
            "filename": "app/logs/gaccess.log",
        },
        "api_file": {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "maxBytes": 10*1024*1024,
            "backupCount": 5,
            "formatter": "generic",
            "filename": "app/logs/gdebug.log",
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'generic',
        },

    },
    'formatters': {
        "generic": {
            "format": "%(asctime)s [%(process)d]: [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }
    }
}

