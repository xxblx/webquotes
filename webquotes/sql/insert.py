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


class InsertUsers(InsertQuery):
    name = 'users'
    cols = ('username', 'password_hash')
