# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

import tornado.web

from .base import WebAuthHandler
from ..sql.insert import InsertQueries


class AddQuoteHandler(WebAuthHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('add.html')

    @tornado.web.authenticated
    async def post(self):
        now = datetime.now()
        title = self.get_argument('quote-title', None)
        text = self.get_argument('quote-text')
        tags = self.get_argument('quote-tags')
        if tags:
            tags = tags.split(',')
        else:
            tags = None

        if not text:
            self.redirect('/add')
            return

        if not title:  # empty str => None
            title = None

        now = mktime(now.utctimetuple())  # unix timestamp
        _quote_args = (title, text, now, self.current_user.decode())
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Insert quote to db and return quote_id
                await cur.execute(InsertQueries.quote, _quote_args)
                _res = await cur.fetchall()

                # Insert new tags and new connections quote-tags to db
                # Repeat %s in query template as many as there are tags
                if tags:
                    _values = ', '.join(['(%s)'] * len(tags))
                    _sql = InsertQueries.quote_tags.format(_values)
                    _tags_args = tags + [_res[0][0], _res[0][0]]
                    await cur.execute(_sql, _tags_args)

        self.redirect('/')
