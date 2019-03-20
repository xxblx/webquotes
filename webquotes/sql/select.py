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

    tokens_auth = """
SELECT
    u.username, t.verify_token
FROM
    tokens t
    INNER JOIN users u
        ON t.user_id = u.user_id
WHERE
    t.select_token = %s
        and
    t.expires_in >= extract(epoch from now())
    """

    tokens_renew = """
SELECT
    u.username, t.verify_token, t.token_id
FROM
    tokens t
    INNER JOIN users u
        ON t.user_id = u.user_id
WHERE
    t.renew_token = %s
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
    array_agg(to_json(t)), 
    r.value
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
        
    INNER JOIN rating r
        ON q.quote_id = r.quote_id
GROUP BY
    q.quote_id, r.value
ORDER BY
    q.datetime DESC
    """

    quotes_by_tag = """
    WITH quotes_ids AS (
        SELECT
            q.quote_id
        FROM
            quotes q 
            INNER JOIN tags_quotes tq
                ON q.quote_id = tq.quote_id
        WHERE
            tq.tag_id = %s
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
        array_agg(to_json(t)),
        r.value
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
        
        INNER JOIN rating r
            ON q.quote_id = r.quote_id 
    GROUP BY
        q.quote_id, r.value
    ORDER BY
        q.datetime DESC
    """

    quote_by_id = """
SELECT
    q.quote_id, 
    quote_title, 
    quote, 
    datetime,
    array_agg(to_json(t)),
    r.value
FROM
    quotes q
    
    LEFT JOIN
    (SELECT
        tq.quote_id,
        tq.tag_id,
        t.tag_name
    FROM
        tags_quotes tq
        INNER JOIN tags t
            ON tq.tag_id = t.tag_id
    WHERE
        tq.quote_id = %s
    ) t
        ON q.quote_id = t.quote_id
        
    INNER JOIN rating r
        ON q.quote_id = r.quote_id
WHERE
    q.quote_id = %s
GROUP BY
    q.quote_id, r.value
    """

    random_quote = """
WITH random_quote as (
    SELECT
        quote_id
    FROM
        quotes
    OFFSET
        floor(
            random() * (
                SELECT 
                    counter_value 
                FROM 
                    data_counters 
                WHERE 
                    counter_name = 'quotes_count'
                ) 
            )
    LIMIT
        1
) 
SELECT
    q.quote_id, 
    quote_title, 
    quote, 
    datetime,
    array_agg(to_json(t)),
    r.value
FROM
    quotes q
    
    INNER JOIN random_quote rq
        ON q.quote_id = rq.quote_id
    
    LEFT JOIN
    (SELECT
        tq.quote_id,
        tq.tag_id,
        t.tag_name
    FROM
        tags_quotes tq
        INNER JOIN random_quote rq
            ON tq.quote_id = rq.quote_id
        
        INNER JOIN tags t
            ON tq.tag_id = t.tag_id
    ) t
        ON q.quote_id = t.quote_id
        
    INNER JOIN rating r
        ON q.quote_id = r.quote_id
GROUP BY
    q.quote_id, r.value
    """

    quote_rating_up = """
SELECT rating_increase(%s)
    """

    quote_rating_down = """
SELECT rating_decrease(%s);
    """
