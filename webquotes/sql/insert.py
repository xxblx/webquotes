# -*- coding: utf-8 -*-


class InsertQuery:
    tmpl = 'INSERT INTO %(name)s (%(cols)s) VALUES(%(values)s)'
    name = None
    cols = None

    @classmethod
    def sql(cls):
        dct = {
            'name': cls.name,
            'cols': ', '.join(cls.cols),
            'values': ', '.join(['%s' for i in cls.cols])
        }
        return cls.tmpl % dct


class InsertFromSelect(InsertQuery):
    tmpl = """
INSERT INTO %(name)s (%(cols)s) 
SELECT %(select_cols)s 
FROM %(select_name)s  
%(where)s 
%(returning)s
"""
    select_name = None
    select_cols = None
    where = None
    returning = None

    @staticmethod
    def get_where(where):
        """ WHERE col = %s and col2 = %s """
        if where:
            return 'WHERE ' + ', '.join(
                ['{} = %s'.format(c) for c in where]
            )
        else:
            return ''

    @staticmethod
    def get_returning(returning):
        """ RETURNING col1, col2 """
        if returning:
            return 'RETURNING ' + ', '.join(returning)
        else:
            return ''

    @classmethod
    def sql(cls):
        dct = {
            'name': cls.name,
            'cols': ', '.join(cls.cols),
            'select_cols': ', '.join(cls.select_cols),
            'select_name': cls.select_name,
            'where': cls.get_where(cls.where),
            'returning': cls.get_returning(cls.returning)
        }
        return cls.tmpl % dct


class InsertUsers(InsertQuery):
    name = 'users'
    cols = ('username', 'password_hash')


class InsertQuotes(InsertFromSelect):
    """ Input args list at query execution should be
    (quote_title, quote, datetime, username)
    """
    name = 'quotes'
    cols = ('quote_title', 'quote', 'user_id', 'datetime')
    select_name = 'users'
    select_cols = ('%s', '%s', 'user_id', '%s')
    where = ('username',)
    returning = ('quote_id',)
