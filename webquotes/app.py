# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
import os.path

import aiopg
import nacl.utils
import tornado.web

from .conf import DEBUG, WORKERS, TOKEN_EXPIRES_TIME
from .handlers.auth import LoginHandler, LogoutHandler
from .handlers.content import (AddQuoteHandler, GetQuoteHandler, RateQuote,
                               GetRandomQuoteHandler)
from .handlers.home import HomeHandler


class WebQuotesApp(tornado.web.Application):
    def __init__(self, loop, db_pool):
        self.loop = loop
        self.db_pool = db_pool

        # Additional pool executor for blocking operations
        self.pool_executor = ThreadPoolExecutor(max_workers=WORKERS)

        handlers = [
            (r'/', HomeHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/add', AddQuoteHandler),
            (r'/quote/([0-9]*/?)', GetQuoteHandler),
            (r'/random', GetRandomQuoteHandler),
            (r'/tag/([0-9]*/?)', HomeHandler),
            (r'/rate/up/([0-9]*/?)', RateQuote),
            (r'/rate/down/([0-9]*/?)', RateQuote)
        ]

        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        static_path = os.path.join(os.path.dirname(__file__), 'static')

        settings = {
            'template_path': template_path,
            'static_path': static_path,
            'login_url': '/login',
            'debug': DEBUG,
            'xsrf_cookies': True,
            'cookie_secret': nacl.utils.random(size=64)
        }

        self.token_expires_time = TOKEN_EXPIRES_TIME
        self.mac_key = nacl.utils.random(size=64)

        super().__init__(handlers, **settings)


async def init_db(dsn):
    """ Connect to database and get initial data

    :param dsn: libpq connection string with parameters
    :type dsn: str
    :return: database connection pool context manager
    """
    return await aiopg.create_pool(dsn=dsn)
