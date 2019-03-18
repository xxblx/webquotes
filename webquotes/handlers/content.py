# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

import tornado.web

from .base import WebAuthHandler
from ..sql.insert import InsertQueries
from ..sql.select import SelectQueries


class AddQuoteHandler(WebAuthHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('add.html')

    @tornado.web.authenticated
    async def post(self):
        now = datetime.now()
        title = self.get_argument('quote-title', None)
        text = self.get_argument('quote-text')
        tags = self.get_argument('quote-tags', None)

        if not text:
            self.redirect('/add')
            return

        if tags:
            tags = tags.split(',')
        # Because html template uses textarea usually the value is
        # an empty string after get_argument
        else:
            tags = None

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


class GetQuoteHandler(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self, quote_id):
        uri = self.request.uri.rstrip('/')
        args = (quote_id.rstrip('/'), quote_id.rstrip('/'))
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.quote_by_id, args)
                _res = await cur.fetchall()

        if _res:
            item = _res[0]
            item = list(item)
            item[3] = datetime.utcfromtimestamp(item[3])
            if item[4][0] is None:  # tags
                item[4] = None

            self.render('quote.html', quote=item, uri=uri)
        else:
            self.redirect('/')


class GetRandomQuoteHandler(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self):
        uri = self.request.uri
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.random_quote)
                _res = await  cur.fetchall()

        if _res:
            item = _res[0]
            item = list(item)
            item[3] = datetime.utcfromtimestamp(item[3])
            if item[4][0] is None:  # tags
                item[4] = None

            self.render('quote.html', quote=item, uri=uri)
        else:
            self.redirect('/')


class RateQuote(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self, quote_id):
        redirect_uri = self.get_argument('next', '/')
        action = self.request.uri.split('/')[2]
        if action == 'up':
            func = SelectQueries.quote_rating_up
        elif action == 'down':
            func = SelectQueries.quote_rating_down

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(func, (quote_id,))

        self.redirect(redirect_uri)
