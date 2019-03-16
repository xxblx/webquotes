# -*- coding: utf-8 -*-


class SelectQuery:
    tmpl = """
SELECT %(cols)s FROM %(name)s 
%(where)s
"""
    name = None
    cols = None
    where = None

    @staticmethod
    def get_where(cols):
        """ WHERE col = %s and col2 = %s """
        if cols:
            return 'WHERE ' + ', '.join(
                ['{} = %s'.format(c) for c in cols]
            )
        else:
            return ''

    @classmethod
    def sql(cls):
        dct = {
            'name': cls.name,
            'cols': ', '.join(cls.cols),
            'where': cls.get_where(cls.where)
        }
        return cls.tmpl % dct


class SelectPasswordHash(SelectQuery):
    name = 'users'
    cols = ('password_hash',)
    where = ('username',)


class SelectUserId(SelectQuery):
    name = 'users'
    cols = ('%s', '%s', 'user_id', '%s')
    where = ('username',)
