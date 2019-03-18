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
        'tag_name': 'TEXT UNIQUE'
    }


class CreateTagsQuotes(CreateQuery):
    name = 'tags_quotes'
    cols_dct = {
        'quote_id': 'SERIAL',
        'tag_id': 'SERIAL'
    }


class CreateDataCounters(CreateQuery):
    name = 'data_counters'
    cols_dct = {
        'row_id': 'SERIAL PRIMARY KEY',
        'counter_name': 'TEXT UNIQUE',
        'counter_value': 'SERIAL'
    }


class Triggers:
    quotes_increase = """
CREATE TRIGGER quotes_increase_trigger 
AFTER INSERT ON quotes
EXECUTE PROCEDURE quotes_increase()
    """

    quotes_decrease = """
CREATE TRIGGER quotes_decrease_trigger 
AFTER DELETE ON quotes
EXECUTE PROCEDURE quotes_decrease()
    """


class Procedures:
    quotes_increase = """
CREATE OR REPLACE FUNCTION quotes_increase() RETURNS TRIGGER AS $example_table$
    BEGIN
        INSERT INTO data_counters(counter_name) 
        VALUES ('quotes_count')
        ON CONFLICT (counter_name)
            DO UPDATE
            SET counter_value = EXCLUDED.counter_value + 1;
        RETURN NEW;
    END;
$example_table$ LANGUAGE plpgsql;
    """

    quotes_decrease = """
CREATE OR REPLACE FUNCTION quotes_decrease() RETURNS TRIGGER AS $example_table$
    BEGIN
        INSERT INTO data_counters(counter_name) 
        VALUES ('quotes_count')
        ON CONFLICT (counter_name)
            DO UPDATE
            SET counter_value = EXCLUDED.counter_value - 1;
        RETURN NEW;
    END;
$example_table$ LANGUAGE plpgsql;  
    """


def get_create_queries():
    modules = sys.modules[__name__]
    for item_name, item in inspect.getmembers(modules, inspect.isclass):
        if item_name != 'CreateQuery' and item_name.startswith('Create'):
            yield item.sql()
