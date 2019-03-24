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

# Address isn't used in the app (e.g. template system) directly
# It is needed for external services like notifications
ADDRESS = 'http://localhost:8888'
EXTERNAL_NOTIFICATIONS = {
    'telegram': {
        'enabled': False,
        'bot_id': 'id',
        'chat_id': 0
    }
}

TG_BOT = {
    'enabled': False,
    'bot_username': 'your_bot_username',
    'bot_id': 'id',
    'chat_id': 0,
    # Keep this token in secret to be sure that only Telegram will
    # send requests to bot url
    'url_token': 'some_secret_token',
    'set_webhook_url': 'https://api.telegram.org/bot%s/setWebhook',
    'delete_webhook_url': 'https://api.telegram.org/bot%s/deleteWebhook',
}
TG_BOT['set_webhook_url'] = TG_BOT['set_webhook_url'] % TG_BOT['bot_id']
TG_BOT['delete_webhook_url'] = TG_BOT['delete_webhook_url'] % TG_BOT['bot_id']
TG_BOT['url'] = ADDRESS + '/tgbot/' + TG_BOT['url_token']
