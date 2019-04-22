# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse

from tornado.httpclient import AsyncHTTPClient

from ..base import BaseHandler
from ...conf import ADDRESS, TG_BOT, TG_BOT_MESSAGES
from ...sql.insert import InsertQueries
from ...sql.select import SelectQueries


class TGBotHandler(BaseHandler):
    def check_xsrf_cookie(self):
        """ Telegram doesn't send _xsrf """
        pass

    @staticmethod
    async def send_message(data):
        """ Send message to telegram chat via POST request

        :param data: POST request parameters
        :type data: dict
        """
        http_client = AsyncHTTPClient()
        body = urlencode(data)
        _url = 'https://api.telegram.org/bot%s/sendMessage'
        await http_client.fetch(
            _url % TG_BOT['bot_id'],
            method='POST',
            body=body
        )

    async def send_quote(self, quote_id, text, rating, title=None, tags=None):
        """ Send message with quote to telegram chat via POST method

        :param quote_id: id of the quote, used in a link to the quote's page
        :type quote_id: int or str
        :param text: the quote itself
        :type text: str
        :param rating: the quote's rating
        :type rating: int
        :param title: title of the quote if exist
        :type title: str or None
        :param tags: a list of tags
        :type tags: list or None
        """
        if title is None:
            title = ''
        else:
            title = '<b>%s</b>' % title

        if tags:
            tags = ' '.join('#%s' % tag['tag_name'] for tag in tags if tag)
        else:
            tags = ''

        message = TG_BOT_MESSAGES['quote'] % {
            'id': quote_id,
            'text': text,
            'rating': rating,
            'title': title,
            'tags': tags,
            'quote_url': '%s/quote/%d' % (ADDRESS, quote_id)
        }
        data = {
            'chat_id': TG_BOT['chat_id'],
            'disable_web_page_preview': False,
            'text': message,
            'parse_mode': 'HTML'
        }
        await self.send_message(data)

    async def rate_quote(self, msg, cmd):
        """ Rate a quote

        :param msg: message with a quote
        :type msg: dict
        :param cmd: action what to do: rate up or rate down
        :type cmd: str
        """
        if not (msg['from']['is_bot'] and 'entities' in msg and
                msg['from']['username'] == TG_BOT['bot_username']):
            return

        # Extract quote_id from url, the url had been inserted into
        # a message via html like when a message was sent
        # <a href="http://localhost:8888/quote/56">#56</a>:
        quote_id = None
        for item in msg['entities']:
            if item['type'] == 'text_link':
                path = urlparse(item['url']).path
                if path.startswith('/quote/'):
                    quote_id = path.split('/')[-1]
                    break

        if quote_id is None:
            return

        if cmd == '/like':
            query = SelectQueries.quote_rating_up
        else:
            query = SelectQueries.quote_rating_down

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (quote_id,))
                _res = await cur.fetchall()

        data = {
            'chat_id': TG_BOT['chat_id'],
            'text': TG_BOT_MESSAGES['rate'] % (int(quote_id), _res[0][0])
        }
        await self.send_message(data)

    async def get_random_quote(self):
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.random_quote)
                _res = await cur.fetchall()

        quote_id, title, text = _res[0][:3]
        tags, rating = _res[0][4:]
        await self.send_quote(quote_id, text, rating, title, tags)

    async def get_quotes(self, ids):
        """ Get quotes by ids from message

        :param ids: a part of the user's message with quotes ids
        :type ids: str
        """
        int_ids = set()
        for item in ids.split(' '):
            if not item:
                continue
            try:
                int_ids.add(int(item))
            except ValueError:
                pass

        for quote_id in int_ids:
            args = (quote_id, quote_id)
            async with self.db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(SelectQueries.quote_by_id, args)
                    _res = await cur.fetchall()

            if _res:
                quote_id, title, text = _res[0][:3]
                tags, rating = _res[0][4:]
                await self.send_quote(quote_id, text, rating, title, tags)

    async def get_top_rated_quotes(self, num=3):
        """ Get top rated quotes

        :param num: how many quotes get
        :type num: int
        """
        args = (0, num)  # offset, num
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.top_rated_quotes, args)
                _res = await cur.fetchall()

        for quote in _res:
            quote_id, title, text = quote[:3]
            tags, rating = quote[4:]
            await self.send_quote(quote_id, text, rating, title, tags)

    async def save_quote(self, msg, tags=None):
        """ Save a quote

        :param msg: user's message for saving as a new quote
        :type msg: dict
        :param tags: a list of tags entered by user via hashtags
            with /save command
        :type tags: list or None
        """
        now = mktime(datetime.now().utctimetuple())  # unix timestamp
        _quote_args = (msg['text'], now)  # text, datetime
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Insert quote to db and return quote_id
                await cur.execute(InsertQueries.quote_bot, _quote_args)
                _res = await cur.fetchall()

        quote_id = _res[0][0]
        if tags:
            tags = ' '.join('#%s' % tag for tag in tags)
        else:
            tags = ''

        message = TG_BOT_MESSAGES['quote'] % {
            'id': quote_id,
            'text': msg['text'],
            'rating': 0,
            'title': '',
            'quote_url': '%s/quote/%d' % (ADDRESS, quote_id),
            'tags': tags
        }
        data = {
            'chat_id': TG_BOT['chat_id'],
            'disable_web_page_preview': False,
            'text': message,
            'parse_mode': 'HTML'
        }
        await self.send_message(data)

    async def show_help(self):
        await self.send_message({
            'chat_id': TG_BOT['chat_id'],
            'text': TG_BOT_MESSAGES['help']
        })

    async def invalid_command(self):
        await self.send_message({
            'chat_id': TG_BOT['chat_id'],
            'text': TG_BOT_MESSAGES['invalid']
        })

    async def post(self):
        update = json.loads(self.request.body)
        if 'message' not in update:
            return
        message = update['message']

        cmds = set()
        if 'entities' in message:
            for item in message['entities']:
                if item['type'] == 'bot_command':
                    _start = item['offset']
                    _stop = item['offset'] + item['length']
                    cmd = message['text'][_start:_stop]
                    cmds.add(cmd)

        if not cmds:
            return

        for cmd in cmds:
            if cmd in ('/like', '/dislike') and 'reply_to_message' in message:
                opposites = {'/like': '/dislike', '/dislike': '/like'}
                opposite_cmd = opposites[cmd]
                if opposite_cmd in cmds:
                    continue
                await self.rate_quote(message['reply_to_message'], cmd)
            elif cmd == '/save' and 'reply_to_message' in message:
                tags = None
                if '#' in message['text']:
                    tags = re.findall('#(\w+)', message['text'])
                await self.save_quote(message['reply_to_message'], tags)
            elif cmd == '/random':
                await self.get_random_quote()
            elif cmd == '/get':
                # Select substring after /get
                _ids = message['text'].split('/get')[1]
                # If the substring is not empty get another substring
                # up to nearest / symbol in case a message has a few commands
                if _ids:
                    _ids = _ids.split('/')[0]
                    await self.get_quotes(_ids)
            elif cmd == '/top':
                num = 3
                _num = re.findall('/top\s*?(\d+)', message['text'])
                if _num:
                    try:
                        _num = int(_num[0])
                        if 1 <= _num <= TG_BOT['top_max_count']:
                            num = _num
                    except ValueError:
                        pass
                await self.get_top_rated_quotes(num)
            elif cmd == '/help':
                await self.show_help()
            else:
                await self.invalid_command()
