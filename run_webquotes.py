#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urlencode
from urllib.request import urlopen

import janus

import tornado.httpserver
import tornado.ioloop

from webquotes.app import WebQuotesApp, init_db
from webquotes.conf import (ADDRESS, DSN, EXTERNAL_NOTIFICATIONS, HOST, PORT,
                            TG_BOT)
from webquotes.notifications.external.manager import run_manager


def main():
    loop = tornado.ioloop.IOLoop.current()
    asyncio_loop = loop.asyncio_loop
    db_pool = loop.asyncio_loop.run_until_complete(init_db(DSN))

    # Set WebHook for Telegram Bot
    if TG_BOT['enabled']:
        urlopen(
            url=TG_BOT['set_webhook_url'],
            data=urlencode({'url': TG_BOT['url']}).encode()
        )

    # If some external notifications backend is enabled, create a queue
    # for notification processing and start external sending worker
    async_queue = None
    sync_queue = None
    if any(item['enabled'] for item in EXTERNAL_NOTIFICATIONS.values()):
        queue = janus.Queue(loop=asyncio_loop)
        notifications_task = asyncio_loop.create_task(
            run_manager(queue.async_q)
        )
        async_queue = queue.async_q
        sync_queue = queue.sync_q
    app = WebQuotesApp(loop, db_pool, async_queue)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT, HOST)

    try:
        loop.start()
    except KeyboardInterrupt:
        if sync_queue:
            sync_queue.put(None)
            asyncio_loop.run_until_complete(notifications_task)
        if TG_BOT['enabled']:
            urlopen(TG_BOT['delete_webhook_url'])
        loop.stop()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
