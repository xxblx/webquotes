# -*- coding: utf-8 -*-


class SelectQuery:
    tmpl = 'SELECT %(cols)s FROM %(name)s %(where)s'
    name = None
    cols = None
    where = None

    @staticmethod
    def get_where(where):
        """
        WHERE col = %s and col2 = %s
        """
        if where:
            return 'WHERE ' + ', '.join(
                ['{} = %s'.format(c) for c in where]
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


class SelectUsers(SelectQuery):
    name = 'users'
    cols = ('password_hash',)
    where = ('username',)
