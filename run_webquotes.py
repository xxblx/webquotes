#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import janus

import tornado.httpserver
import tornado.ioloop

from webquotes.app import WebQuotesApp, init_db
from webquotes.conf import DSN, EXTERNAL_NOTIFICATIONS, HOST, PORT
from webquotes.notifications.external.manager import run_manager


def main():
    loop = tornado.ioloop.IOLoop.current()
    asyncio_loop = loop.asyncio_loop
    db_pool = loop.asyncio_loop.run_until_complete(init_db(DSN))

    # If some external notifications backend is enabled, create a queue
    # for notification processing and start external sending worker
    queue = None
    if any(item['enabled'] for item in EXTERNAL_NOTIFICATIONS.values()):
        queue = janus.Queue(loop=asyncio_loop)
        notifications_task = asyncio_loop.create_task(
            run_manager(queue.async_q)
        )
    app = WebQuotesApp(loop, db_pool, queue.async_q)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT, HOST)

    try:
        loop.start()
    except KeyboardInterrupt:
        queue.sync_q.put(None)
        asyncio_loop.run_until_complete(notifications_task)
        loop.stop()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
