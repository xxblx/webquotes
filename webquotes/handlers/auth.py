# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web

from .base import WebAuthHandler
from ..sql.select import SelectPasswordHash


class LoginHandler(WebAuthHandler):
    def get(self):
        if self.get_current_user():
            self.redirect('/')
        else:
            self.render('login.html')

    async def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectPasswordHash.sql(), (username,))
                _res = await cur.fetchall()

        if _res:
            password_check = await self.verify_password(
                _res[0][0].tobytes(),
                tornado.escape.utf8(password)
            )

        if not _res or not password_check:
            raise tornado.web.HTTPError(403, 'invalid username or password')

        self.set_secure_cookie('username', username)
        self.redirect(self.get_argument('next', '/'))


class LogoutHandler(WebAuthHandler):
    def get(self):
        if self.get_current_user():
            self.clear_cookie('username')
        self.redirect(self.get_argument('next', '/'))
