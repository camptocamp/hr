# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests

from openerp import api, fields, models
from openerp import exceptions


class NetworkApi(models.Model):
    _name = 'bso.network.api'

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    url = fields.Char(required=True)
    user = fields.Char(required=True)
    password = fields.Char(required=True)
    path = fields.Char(required=True)

    @api.multi
    def test_connection(self):
        self.ensure_one()
        try:
            r = requests.get('%(url)s/%(path)s' % {'url': self.url,
                                                   'path': self.path
                                                   },
                             auth=(self.user, self.password),
                             verify=False)
            if r.status_code != 200:
                raise exceptions.UserError(r.status_code + ' ' + r.reason)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.UserError(e.message)

        return True

    @api.multi
    def call(self, start, end, sort=1, backup=1, details=1):
        """ @param::sort INTEGER :: 1=latency, 2=mrc, 3=latency/mrc"""
        self.ensure_one()
        payload = {'start': start,
                   'end': end,
                   'sort': sort,
                   'backup': backup,
                   'details': details}

        r = requests.get('%(url)s/%(path)s' % {'url': self.url,
                                               'path': self.path
                                               },
                         auth=(self.user, self.password),
                         verify=False,
                         params=payload)
        return r.json()

    @api.multi
    def test_call(self):
        """ start=SYD-ASX&end=AMS-TEL2&sort=1&backup=1&details=1 """
        self.ensure_one()
        res = self.call('SYD-ASX', 'AMS-TEL2', sort=1, backup=1, details=1)
        res2 = self.call('SYD-ASX', 'AMS-TEL2', sort=1, backup=1, details=0)
        print res
        print "*"*80
        print res2
        return res
