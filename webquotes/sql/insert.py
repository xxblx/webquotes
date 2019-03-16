# -*- coding: utf-8 -*-

class InsertQueries:
    users = """
INSERT INTO users (username, password_hash) VALUES (%s, %s)
    """

    quote = """
INSERT INTO quotes (quote_title, quote, user_id, datetime) 
SELECT
    %s, %s, user_id, %s
FROM
    users
WHERE
    username = %s
RETURNING 
    quote_id
    """
