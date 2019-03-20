# -*- coding: utf-8 -*-

from ...conf import EXTERNAL_NOTIFICATIONS
from .tg import TelegramBackend


class NotificationsManager:
    def __init__(self):
        self.backends = set()

        if EXTERNAL_NOTIFICATIONS['telegram']['enabled']:
            kw = EXTERNAL_NOTIFICATIONS['telegram']
            kw.pop('enabled')
            tg_backend = TelegramBackend(**kw)
            self.backends.add(tg_backend)

    async def send_notification(self, quote_id, text, title=None):
        for backend in self.backends:
            await backend.send_notification(quote_id, text, title)


async def run_manager(queue):
    manager = NotificationsManager()
    item = await queue.get()
    while item is not None:
        await manager.send_notification(*item)
        item = await queue.get()
