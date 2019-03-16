# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

import tornado.web

from .base import WebAuthHandler
from ..sql.insert import InsertQuotes

class AddQuoteHandler(WebAuthHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('add.html')

    @tornado.web.authenticated
    async def post(self):
        now = datetime.now()
        title = self.get_argument('quote-title', None)
        text = self.get_argument('quote-text')

        if not text:
            self.redirect('/add')
            return

        if not title:  # empty str => None
            title = None

        now = mktime(now.utctimetuple())  # unix timestamp
        args = (title, text, now, self.current_user.decode())
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(InsertQuotes.sql(), args)
                # TODO: tags

        self.redirect('/')
