# -*- coding: utf-8 -*-

import tornado.web

from .base import WebAuthHandler


class HomeHandler(WebAuthHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('home.html')
