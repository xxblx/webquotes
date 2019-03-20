# -*- coding: utf-8 -*-

import nacl.exceptions
import nacl.pwhash

import tornado.web
import tornado.concurrent


class BaseHandler(tornado.web.RequestHandler):
    @property
    def loop(self):
        return self.application.loop

    @property
    def pool_executor(self):
        return self.application.pool_executor

    @property
    def db_pool(self):
        return self.application.db_pool

    @property
    def queue(self):
        return self.application.queue

    async def verify_password(self, hashed, password):
        """ Compare entered password with exist password hash

        :param hashed: a hash of a password
        :type hashed: bytes
        :param password: a password entered by a user
        :type password: bytes
        :return: False if the password is wrong, otherwise - True
        """
        try:
            return await self.loop.run_in_executor(
                self.pool_executor,
                nacl.pwhash.verify,
                hashed,
                password
            )
        except nacl.exceptions.InvalidkeyError:
            return False


class WebAuthHandler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username')
