# -*- coding: utf-8 -*-

import inspect
import sys


class CreateQuery:
    tmpl = 'CREATE TABLE IF NOT EXISTS %(name)s (%(cols)s)'
    name = None
    cols_dct = None

    @staticmethod
    def get_cols(dct):
        return ', '.join(['%s %s' % (col, dct[col]) for col in dct])

    @classmethod
    def sql(cls):
        cols = cls.get_cols(cls.cols_dct)
        return cls.tmpl % {'name': cls.name, 'cols': cols}


class CreateUsers(CreateQuery):
    name = 'users'
    cols_dct = {
        'user_id': 'SERIAL PRIMARY KEY',
        'username': 'TEXT',
        'password_hash': 'BYTEA'
    }


class CreateGroups(CreateQuery):
    name = 'groups'
    cols_dct = {
        'group_id': 'SERIAL PRIMARY KEY',
        'group_name': 'TEXT'
    }


class CreateGroupsUsers(CreateQuery):
    name = 'groups_users'
    cols_dct = {
        'group_id': 'SERIAL',
        'user_id': 'SERIAL'
    }


class CreateTokens(CreateQuery):
    name = 'tokens'
    cols_dct = {
        'token_id': 'SERIAL PRIMARY KEY',
        'user_id': 'SERIAL',
        'select_token': 'TEXT',
        'verify_token': 'BYTEA',
        'renew_token': 'TEXT',
        'expires_in': 'INTEGER'
    }


class CreateQuotes(CreateQuery):
    name = 'quotes'
    cols_dct = {
        'quote_id': 'SERIAL PRIMARY KEY',
        'quote_title': 'TEXT DEFAULT NULL',
        'quote': 'TEXT',
        'user_id': 'SERIAL',
        'datetime': 'INTEGER'
    }


class CreateGroupsQuotes(CreateQuery):
    name = 'groups_quotes'
    cols_dct = {
        'quote_id': 'SERIAL',
        'group_id': 'SERIAL'
    }


class CreateTags(CreateQuery):
    name = 'tags'
    cols_dct = {
        'tag_id': 'SERIAL PRIMARY KEY',
        'tag_name': 'TEXT'
    }


class CreateTagsQuotes(CreateQuery):
    name = 'tags_quotes'
    cols_dct = {
        'quote_id': 'SERIAL',
        'tag_id': 'SERIAL'
    }


def get_create_queries():
    modules = sys.modules[__name__]
    for item_name, item in inspect.getmembers(modules, inspect.isclass):
        if item_name != 'CreateQuery' and item_name.startswith('Create'):
            yield item.sql()
