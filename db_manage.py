#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getpass
import argparse

import nacl.pwhash
import psycopg2

from webquotes.conf import DSN
from webquotes.sql.create import get_create_queries
from webquotes.sql.insert import InsertUsers


def create_tables():
    queries = get_create_queries()
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            for q in queries:
                cur.execute(q)


def create_user(username):
    password = getpass.getpass()
    hashed = nacl.pwhash.str(password.encode())
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(InsertUsers.sql(), (username, hashed))


COMMANDS = {
    'init': {
        'func': create_tables,
        'kw': []
    },
    'user-add': {
        'func': create_user,
        'kw': ['username']
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
