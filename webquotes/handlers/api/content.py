# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime

import tornado.web

from .base import ApiHandler
from ...sql.insert import InsertQueries
from ...sql.select import SelectQueries


class APIAddQuoteHandler(ApiHandler):
    async def post(self):
        now = datetime.now()
        try:
            text = self.get_argument('text')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(400)
        title = self.get_argument('title', None)
        tags = self.get_arguments('tag')

        now = mktime(now.utctimetuple())  # unix timestamp
        _quote_args = (title, text, now, self.current_user['username'])
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

        # Send external notifications
        if self.queue is not None:
            _args = (_res[0][0], text, title)
            await self.queue.put(_args)

        self.write({'quote_id': _res[0][0]})


class APIGetQuotesHandler(ApiHandler):
    async def get(self):
        quote_id = self.get_argument('quote_id', None)
        tag_id = self.get_argument('tag_id', None)
        offset = int(self.get_argument('offset', 0))
        num = int(self.get_argument('num', 100))
        if not (0 < num <= 500):
            num = 100

        # Get one quote by id
        if quote_id is not None:
            args = (quote_id, quote_id)
            query = SelectQueries.quote_by_id
        # Get N quotes with tag by tag_id, where N == num
        elif tag_id is not None:
            args = (tag_id, offset, num)
            query = SelectQueries.quotes_by_tag
        # Get N quotes
        else:
            args = (offset, num)
            query = SelectQueries.quotes

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                _res = await cur.fetchall()
                keys = [col.name for col in cur.description]

        # Make a dict with the results for JSON sending to the client
        results = {
            'data': [],
            'count': len(_res)
        }
        for row in _res:
            dct = {keys[i]: row[i] for i in range(len(keys))}
            results['data'].append(dct)
        self.write(results)


class APIGetRandomQuote(ApiHandler):
    async def get(self):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.random_quote)
                _res = await cur.fetchall()
                keys = [col.name for col in cur.description]

        # Make a dict with the results for JSON sending to the client
        results = {
            'data': [],
            'count': len(_res)
        }
        for row in _res:
            dct = {keys[i]: row[i] for i in range(len(keys))}
            results['data'].append(dct)
        self.write(results)


class APIGetTopRatedQuotesHandler(ApiHandler):
    async def get(self):
        offset = int(self.get_argument('offset', 0))
        num = int(self.get_argument('num', 100))
        if not (0 < num <= 500):
            num = 100

        # Get N quotes
        args = (offset, num)
        query = SelectQueries.top_rated_quotes

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                _res = await cur.fetchall()
                keys = [col.name for col in cur.description]

        # Make a dict with the results for JSON sending to the client
        results = {
            'data': [],
            'count': len(_res)
        }
        for row in _res:
            dct = {keys[i]: row[i] for i in range(len(keys))}
            results['data'].append(dct)
        self.write(results)


class APIRateQuoteHandler(ApiHandler):
    async def post(self):
        try:
            action = self.get_argument('action')
            quote_id = self.get_argument('quote_id')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(400)

        if action not in ('up', 'down'):
            raise tornado.web.HTTPError(400)
        if action == 'up':
            query = SelectQueries.quote_rating_up
        else:
            query = SelectQueries.quote_rating_down

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (quote_id,))


class APIGetTagsHandler(ApiHandler):
    async def get(self):
        offset = int(self.get_argument('offset', 0))
        num = int(self.get_argument('num', 100))
        if not (0 < num <= 500):
            num = 100

        # Get N tags
        args = (offset, num)
        query = SelectQueries.tags_limited

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                _res = await cur.fetchall()
                keys = [col.name for col in cur.description]

        # Make a dict with the results for JSON sending to the client
        results = {
            'data': [],
            'count': len(_res)
        }
        for row in _res:
            dct = {keys[i]: row[i] for i in range(len(keys))}
            results['data'].append(dct)
        self.write(results)
