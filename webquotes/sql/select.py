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

    # WITH at the beginning is needed for limiting internal rows selection
    # from tags and quotes_tags tables, e.g. for selecting only tags used
    # with this quotes
    quotes = """
WITH quotes_ids AS (
    SELECT
        quote_id
    FROM
        quotes
    ORDER BY
        datetime DESC
    OFFSET %s ROWS
    FETCH FIRST %s ROWS ONLY
)

SELECT
    q.quote_id, 
    quote_title, 
    quote, 
    datetime, 
    array_agg(to_json(t))
FROM
    quotes q
    
    INNER JOIN quotes_ids qi
        ON q.quote_id = qi.quote_id
    
    LEFT JOIN
    (SELECT
        tq.quote_id, 
        tq.tag_id,
        t.tag_name
    FROM
        tags_quotes tq 
        INNER JOIN tags t
            ON tq.tag_id = t.tag_id
        
        INNER JOIN quotes_ids qi
            ON tq.quote_id = qi.quote_id
    ) t
        ON q.quote_id = t.quote_id
GROUP BY
    q.quote_id
ORDER BY
    q.datetime DESC
    """
