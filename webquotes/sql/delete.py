# -*- coding: utf-8 -*-

class DeleteQueries:
    tokens = """
DELETE FROM tokens WHERE token_id = %s
    """
