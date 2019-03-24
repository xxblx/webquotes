# -*- coding: utf-8 -*-

import pprint
import json

from ..base import BaseHandler


class TGBotHandler(BaseHandler):
    def check_xsrf_cookie(self):
        """ Telegram doesn't send _xsrf """
        pass

    @property
    def tg_bot(self):
        return self.application.tg_bot

    def post(self):
        update = json.loads(self.request.body)
        if 'message' not in update:
            return
        message = update['message']

        cmds = set()
        if 'entities' in message:
            for item in message['entities']:
                if item['type'] == 'bot_command':
                    _start = item['offset']
                    _stop = item['offset'] + item['length']
                    cmd = message['text'][_start:_stop]
                    cmds.add(cmd)

        if not cmds:
            return

        for cmd in cmds:
            if cmd == '/like' and '/dislike' not in cmds:
                pass
            elif cmd == '/dislike' and '/like' not in cmds:
                pass
            elif cmd == '/random':
                pass
            elif cmd == '/save':
                pass
            elif cmd == '/help':
                pass
            else:
                # Invalid command
                pass
