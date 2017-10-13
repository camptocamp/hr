# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import models, api
import requests


class ServiceNotFound(Exception):
    pass


class BSOWS(models.AbstractModel):
    _name = 'bso.ws'

    REQUESTS_TIMEOUT = 10
    ENDPOINTS = {
        # TODO: get info from customer
        'invoice/extralines': '/invoices/extra',
        'invoice/info': '/invoices/info',
    }
    BASE_URL = 'https://bso.test.ws'

    @api.model
    def ws_get_client(self):
        session = requests.Session()
        # TODO: do we have credentials?
        session.headers['Content-Type'] = 'application/json'
        return session

    def ws_get(self, key, data):
        url = self._ws_url_for(key, data['id'])
        return self._ws_get(url, data)

    def _ws_get(self, url, data):
        client = self.ws_get_client()
        return client.get(url, json=data, verify=False,
                          timeout=self.REQUESTS_TIMEOUT)

    def _ws_url_for(self, key, ext_id):
        try:
            return self.BASE_URL + self.ENDPOINTS[key] + '/' + str(ext_id)
        except KeyError:
            raise ServiceNotFound(key)
