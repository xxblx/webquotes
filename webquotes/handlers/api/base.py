# -*- coding: utf-8 -*-

import functools

from nacl.bindings.utils import sodium_memcmp
import nacl.encoding
import nacl.hash
import tornado.escape
import tornado.web

from ..base import BaseHandler
from ...sql.select import SelectQueries


class BaseApiHandler(BaseHandler):
    @property
    def mac_key(self):
        return self.application.mac_key

    def check_xsrf_cookie(self):
        """ Don't verify _xsrf when token-based access is using """
        pass

    async def hash_token(self, token, mac_key=None):
        """ Get hash of a token

        :param token: a token for hashing
        :type token: str
        :param mac_key: a key for message authentication (hmac)
        :type mac_key: bytes
        :return: hex encoded hash of the token
        :rtype: bytes
        """
        return await self.loop.run_in_executor(
            self.pool_executor,
            # functools.partial used to pass keyword arguments to function
            functools.partial(
                # function
                nacl.hash.blake2b,
                # keyword args
                data=tornado.escape.utf8(token),
                key=mac_key,
                encoder=nacl.encoding.HexEncoder
            )
        )

    async def check_verify_token(self, plain_token, hashed_token):
        """ Check given plain-text token with a hashed one

        :param plain_token: verify token in plain text provided by user
        :type plain_token: str
        :param hashed_token: verify token selected from db
        :type hashed_token: bytes
        :return: True if hashed_token equals hash of plain_token
        :rtype: bool
        """
        _hashed = await self.hash_token(plain_token, self.mac_key)
        return await self.loop.run_in_executor(
            self.pool_executor, sodium_memcmp, hashed_token, _hashed
        )


class ApiHandler(BaseApiHandler):
    async def prepare(self):
        self.current_user = None
        try:
            select_token = self.get_argument('select_token')
            verify_token = self.get_argument('verify_token')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(403, 'invalid tokens')

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.tokens_auth, (select_token,))
                _res = await cur.fetchall()

        check = False
        if _res:
            username = _res[0][0]
            verify_token_hashed = _res[0][1].tobytes()
            check = await self.check_verify_token(verify_token,
                                                  verify_token_hashed)
        if not check:
            raise tornado.web.HTTPError(403, 'invalid tokens')

        self.current_user = {
            'username': username,
            'select_token': select_token
        }


class TestApiHandler(ApiHandler):
    def post(self):
        self.write('hello world')
