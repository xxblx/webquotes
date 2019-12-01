# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor
import os.path

import aiopg
import nacl.utils
import tornado.web

from .conf import DEBUG, WORKERS, TOKEN_EXPIRES_TIME, TG_BOT

from .handlers.auth import LoginHandler, LogoutHandler
from .handlers.content import (AddQuoteHandler, GetRandomQuoteHandler,
                               GetQuoteHandler, RateQuoteHandler, TagsHandler)
from .handlers.home import HomeHandler

from .handlers.api.base import TestApiHandler
from .handlers.api.content import (APIAddQuoteHandler, APIGetRandomQuote,
                                   APIGetTopRatedQuotesHandler,
                                   APIGetQuotesHandler, APIRateQuoteHandler,
                                   APIGetTagsHandler)
from .handlers.api.tokens import GetTokensHandler, RenewTokensHandler

from .handlers.tgbot.base import TGBotHandler


class WebQuotesApp(tornado.web.Application):
    tg_bot = None

    def __init__(self, loop, db_pool, queue=None):
        self.loop = loop
        self.db_pool = db_pool
        self.queue = queue

        # Additional pool executor for blocking operations
        self.pool_executor = ThreadPoolExecutor(max_workers=WORKERS)

        handlers = [
            (r'/', HomeHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/add', AddQuoteHandler),
            (r'/quote/([0-9]*/?)', GetQuoteHandler),
            (r'/random', GetRandomQuoteHandler),
            (r'/tags', TagsHandler),
            (r'/tag/([0-9]*/?)', HomeHandler),
            (r'/top', HomeHandler),
            (r'/rate/up/([0-9]*/?)', RateQuoteHandler),
            (r'/rate/down/([0-9]*/?)', RateQuoteHandler),

            (r'/api/tokens/get', GetTokensHandler),
            (r'/api/tokens/renew', RenewTokensHandler),

            (r'/api/quotes/add', APIAddQuoteHandler),
            (r'/api/quotes/get', APIGetQuotesHandler),
            (r'/api/quotes/random', APIGetRandomQuote),
            (r'/api/quotes/top', APIGetTopRatedQuotesHandler),
            (r'/api/quotes/rate', APIRateQuoteHandler),

            (r'/api/tags/get', APIGetTagsHandler)
        ]
        if DEBUG:
            handlers.append((r'/api/test', TestApiHandler))
        if TG_BOT['enabled']:
            self.tg_bot = TG_BOT
            handlers.append((r'/tgbot/' + TG_BOT['url_token'], TGBotHandler))

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
