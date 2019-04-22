# -*- coding: utf-8 -*-

from datetime import datetime

import tornado.web

from .base import WebAuthHandler
from ..sql.select import SelectQueries


class HomeHandler(WebAuthHandler):
    @tornado.web.authenticated
    async def get(self, tag_id=None):
        offset = int(self.get_argument('offset', 0))
        num = int(self.get_argument('num', 100))
        if num > 100 or num < 0:
            num = 100

        # host/tag/num
        if self.request.uri.startswith('/tag') and tag_id is not None:
            args = (tag_id.rstrip('/'), offset, num)
            sql = SelectQueries.quotes_by_tag
            uri = '/tag/%s' % tag_id.rstrip('/')
        # host/top/
        elif self.request.uri.startswith('/top'):
            args = (offset, num)
            sql = SelectQueries.top_rated_quotes
            uri = '/top'
        # host/
        else:
            args = (offset, num)
            sql = SelectQueries.quotes
            uri = '/'

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, args)
                _res = await cur.fetchall()

        quotes_data = []
        for item in _res:
            item = list(item)
            item[3] = datetime.utcfromtimestamp(item[3])
            if item[4][0] is None:
                item[4] = None
            quotes_data.append(item)

        next_offset = offset+num
        self.render('home.html', quotes_data=quotes_data, quotes_num=num,
                    next_offset=next_offset, uri=uri)
