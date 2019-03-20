# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from time import mktime
from uuid import uuid4

import tornado.web

from .base import BaseApiHandler
from ...sql.delete import DeleteQueries
from ...sql.insert import InsertQueries
from ...sql.select import SelectQueries


class BaseTokensHandler(BaseApiHandler):
    @property
    def token_expires_time(self):
        return self.application.token_expires_time

    async def generate_tokens(self, username):
        """ Generate three new tokens for a user with given username:
            * select_token used in select queries in db.
            * verify_token used for verification of select and renew tokens.
                verify_token isn't stored directly in db. Instead of that
                hash of the token stored. In case of unexpected read access
                to db (e.g. theft of db dump, injection, etc) plain
                verify_token isn't going to be compromised, it makes
                all stolen tokens useless because only the app knows mac key
                used for hashing and the app always hashes the content of
                the verify_token argument of post request.
            * renew_token used for one-time issuing new three tokens.

        :return: a dict with tokens
        """
        select_token = uuid4().hex
        verify_token = uuid4().hex
        renew_token = uuid4().hex
        expires_in = datetime.now() + timedelta(seconds=self.token_expires_time)
        expires_in = mktime(expires_in.utctimetuple())

        # verify_token stores as a hash instead of plain-text
        verify_token_hash = await self.hash_token(verify_token, self.mac_key)
        args = (select_token, verify_token_hash, renew_token, expires_in,
                username)
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(InsertQueries.tokens, args)

        tokens = {
            'select_token': select_token,
            'verify_token': verify_token,
            'renew_token': renew_token,
            'expires_in': expires_in
        }
        return tokens


class GetTokensHandler(BaseTokensHandler):
    async def post(self):
        try:
            username = self.get_argument('username')
            password = self.get_argument('password')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(400)

        check = await self.check_user(username, password)
        if not check:
            raise tornado.web.HTTPError(403, 'invalid username or password')

        tokens = await self.generate_tokens(username)
        self.write(tokens)


class RenewTokensHandler(BaseTokensHandler):
    async def post(self):
        try:
            renew_token = self.get_argument('renew_token')
            verify_token = self.get_argument('verify_token')
        except tornado.web.MissingArgumentError:
            raise tornado.web.HTTPError(403, 'invalid tokens')

        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(SelectQueries.tokens_renew, (renew_token,))
                _res = await cur.fetchall()

        check = False
        if _res:
            username = _res[0][0]
            verify_token_hashed = _res[0][1].tobytes()
            token_id = _res[0][2]
            check = await self.check_verify_token(verify_token,
                                                  verify_token_hashed)
        if not check:
            raise tornado.web.HTTPError(403, 'invalid tokens')

        # Delete used tokens
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(DeleteQueries.tokens, (token_id,))

        tokens = await self.generate_tokens(username)
        self.write(tokens)
