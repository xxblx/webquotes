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
        'user_id': 'SERIAL PRIMARY KEY CHECK (user_id != -1)',
        'username': 'TEXT UNIQUE',
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
        'user_id': 'INTEGER',
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
        'counter_value': 'INTEGER'
    }


class CreateRating(CreateQuery):
    name = 'rating'
    cols_dct = {
        'quote_id': 'SERIAL UNIQUE',
        'value': 'INTEGER'
    }


class Triggers:
    quotes_increase = """
CREATE TRIGGER quotes_increase_trigger 
AFTER INSERT ON quotes
FOR EACH ROW
EXECUTE PROCEDURE quotes_increase()
    """

    quotes_decrease = """
CREATE TRIGGER quotes_decrease_trigger 
AFTER DELETE ON quotes
FOR EACH ROW
EXECUTE PROCEDURE quotes_decrease()
    """

    rating = """
CREATE TRIGGER rating_trigger
AFTER INSERT ON quotes
FOR EACH ROW
EXECUTE PROCEDURE new_rating()
    """


class Procedures:
    quotes_increase = """
CREATE OR REPLACE FUNCTION quotes_increase() RETURNS TRIGGER AS $BODY$
    BEGIN
        INSERT INTO data_counters(counter_name) 
        VALUES ('quotes_count')
        ON CONFLICT (counter_name)
            DO UPDATE
            SET counter_value = data_counters.counter_value + 1;
        RETURN NEW;
    END;
$BODY$ LANGUAGE plpgsql;
    """

    quotes_decrease = """
CREATE OR REPLACE FUNCTION quotes_decrease() RETURNS TRIGGER AS $BODY$
    BEGIN
        INSERT INTO data_counters(counter_name) 
        VALUES ('quotes_count')
        ON CONFLICT (counter_name)
            DO UPDATE
            SET counter_value = data_counters.counter_value - 1;
        RETURN NEW;
    END;
$BODY$ LANGUAGE plpgsql;  
    """

    rating_increase = """
CREATE OR REPLACE FUNCTION rating_increase(_quote_id INT) RETURNS INT AS $BODY$
    BEGIN         
        INSERT INTO rating(quote_id)
        VALUES (_quote_id)
        ON CONFLICT (quote_id)
            DO UPDATE
            SET value = rating.value + 1;
        RETURN (SELECT value FROM rating WHERE quote_id = _quote_id);
    END;
$BODY$ LANGUAGE plpgsql;
    """

    rating_decrease = """
CREATE OR REPLACE FUNCTION rating_decrease(_quote_id INT) RETURNS INT AS $BODY$
    BEGIN         
        INSERT INTO rating(quote_id)
        VALUES (_quote_id)
        ON CONFLICT (quote_id)
            DO UPDATE
            SET value = rating.value - 1;
        RETURN (SELECT value FROM rating WHERE quote_id = _quote_id);
    END;
$BODY$ LANGUAGE plpgsql;
    """

    new_rating = """
CREATE OR REPLACE FUNCTION new_rating() RETURNS TRIGGER AS $BODY$
    BEGIN
        INSERT INTO rating(quote_id, value) 
        VALUES (NEW.quote_id, 0);
        RETURN NEW;
    END;
$BODY$ LANGUAGE plpgsql;
    """


def get_create_queries():
    modules = sys.modules[__name__]
    for item_name, item in inspect.getmembers(modules, inspect.isclass):
        if item_name != 'CreateQuery' and item_name.startswith('Create'):
            yield item.sql()
