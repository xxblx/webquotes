#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from time import mktime
import argparse
import getpass

import nacl.pwhash
import psycopg2

from webquotes.conf import DSN
from webquotes.sql.create import get_create_queries, Triggers, Procedures
from webquotes.sql.insert import InsertQueries


def init_db():
    queries = get_create_queries()
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            # Create tables
            for q in queries:
                cur.execute(q)

            # Create functions and triggers
            cur.execute(Procedures.quotes_increase)
            cur.execute(Procedures.quotes_decrease)
            cur.execute(Procedures.rating_increase)
            cur.execute(Procedures.rating_decrease)
            cur.execute(Procedures.new_rating)
            cur.execute(Triggers.quotes_decrease)
            cur.execute(Triggers.quotes_increase)
            cur.execute(Triggers.rating)

            # Insert values to "service" table with counters
            cur.execute(InsertQueries.counter_quotes)


def create_user(username):
    password = getpass.getpass()
    hashed = nacl.pwhash.str(password.encode())
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(InsertQueries.users, (username, hashed))


def insert_quote(title, text, username):
    now = mktime(datetime.now().utctimetuple())
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            args = (title, text, now, username)
            cur.execute(InsertQueries.quote, args)
            quote_id = cur.fetchall()[0][0]
    print(quote_id)


COMMANDS = {
    'init': {
        'func': init_db,
        'kw': []
    },
    'user-add': {
        'func': create_user,
        'kw': ['username']
    },
    'quote-add': {
        'func': insert_quote,
        'kw': ['title', 'text', 'username']
    }
}


def main():
    parser = argparse.ArgumentParser(prog='webquotes-manager-cli')
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(used='init')

    user_add_parser = subparsers.add_parser('user-add')
    user_add_parser.set_defaults(used='user-add')
    user_add_parser.add_argument('-u', '--username', type=str, required=True)

    quote_add_parser = subparsers.add_parser('quote-add')
    quote_add_parser.set_defaults(used='quote-add')
    quote_add_parser.add_argument('-T', '--title', type=str, default=None)
    quote_add_parser.add_argument('-t', '--text', type=str, required=True)
    quote_add_parser.add_argument('-u', '--username', type=str, default=None)

    args = parser.parse_args()
    if 'used' not in args:
        return
    else:
        _args = vars(args)
        func = COMMANDS[args.used]['func']
        kw = {k: _args[k] for k in COMMANDS[args.used]['kw']}
        func(**kw)


if __name__ == '__main__':
    main()
