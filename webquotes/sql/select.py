# -*- coding: utf-8 -*-


class SelectQueries:
    users = """
SELECT
    password_hash
FROM
    users
WHERE
    username = %s    
"""
