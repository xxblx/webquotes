# -*- coding: utf-8 -*-


class InsertQueries:
    users = """
INSERT INTO users (username, password_hash) VALUES (%s, %s)
    """

    tokens = """
INSERT INTO 
    tokens (user_id, select_token, verify_token, renew_token, expires_in)
SELECT
    user_id, %s, %s, %s, %s
FROM
    users
WHERE
    username = %s
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

    quote_bot = """
INSERT INTO quotes (quote, user_id, datetime) 
VALUES (%s, -1, %s)
RETURNING 
    quote_id  
    """

    quote_tags = """   
WITH
    provided_tags(tag_name) as (
        VALUES {}
    ),
    exist_tags as (
        SELECT
            tag_id
        FROM
            tags INNER JOIN provided_tags 
                ON tags.tag_name = provided_tags.tag_name
    ), 
    new_tags as (
        INSERT INTO tags 
            (tag_name) 
        SELECT
            tag_name
        FROM
            provided_tags
        ON CONFLICT 
            (tag_name)
            DO NOTHING
        RETURNING 
            tag_id
    )

INSERT INTO tags_quotes (quote_id, tag_id)

SELECT
    %s, tag_id
FROM
    exist_tags

UNION ALL

SELECT
    %s, tag_id
FROM
    new_tags
    """

    counter_quotes = """
INSERT INTO data_counters (counter_name, counter_value)
VALUES ('quotes_count', 0)
    """
