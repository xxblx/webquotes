# -*- coding: utf-8 -*-

from urllib.parse import urlencode

from tornado.httpclient import AsyncHTTPClient

from ...conf import ADDRESS


class TelegramBackend:
    base_url = 'https://api.telegram.org/bot%s/sendMessage'
    tmpl = """
<a href="%(quote_url)s">#%(id)d</a>: %(title)s
%(text)s
Rating: 0
%(tags)s
"""

    def __init__(self, bot_id, chat_id):
        self.http_client = AsyncHTTPClient()
        self.chat_id = chat_id
        self.url = self.base_url % bot_id

    async def send_notification(self, quote_id, text, title, tags):
        if title is None:
            title = ''
        else:
            title = '<b>%s</b>' % title

        if tags:
            tags = ' '.join('#%s' % tag for tag in tags)
        else:
            tags = ''

        message = self.tmpl % {
            'id': quote_id,
            'text': text,
            'title': title,
            'tags': tags,
            'quote_url': '%s/quote/%d' % (ADDRESS, quote_id)
        }
        data = {
            'chat_id': self.chat_id,
            'disable_web_page_preview': False,
            'text': message,
            'parse_mode': 'HTML'
        }
        body = urlencode(data)
        await self.http_client.fetch(self.url, method='POST', body=body)
