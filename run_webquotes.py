#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop

from webquotes.app import WebQuotesApp, init_db
from webquotes.conf import DSN, HOST, PORT


def main():
    loop = tornado.ioloop.IOLoop.current()
    db_pool = loop.asyncio_loop.run_until_complete(init_db(DSN))
    app = WebQuotesApp(loop, db_pool)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(PORT, HOST)

    try:
        loop.start()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
