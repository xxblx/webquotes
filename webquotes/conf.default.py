# -*- coding: utf-8 -*-

import multiprocessing

# Database
DB_SETTINGS = {
    'name': 'quotes',
    'user': 'quotesuser',
    'password': 'hello_i_am_a_password',
    'host': '127.0.0.1'
}
DSN = 'dbname=%(name)s user=%(user)s password=%(password)s host=%(host)s'
DSN = DSN % DB_SETTINGS

# HTTP Server
HOST = '127.0.0.1'
PORT = 8888

# Web application
WORKERS = multiprocessing.cpu_count()
TOKEN_EXPIRES_TIME = 7200  # seconds
DEBUG = False
REGISTRATION = False  # allow to users create new accounts
