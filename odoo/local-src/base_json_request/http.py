# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http

old_init = http.JsonRequest.__init__


def __init__(self, *args):
    try:
        old_init(self, *args)
    except AttributeError, e:
        try:
            self.jsonrequest = {'params': self.jsonrequest, 'id': False}
            self.params = dict(self.jsonrequest)
            self.context = dict(self.session.context)
        except ValueError:
            raise e
