# -*- coding: utf-8 -*-
import logging

import requests
from odoo import models

_logger = logging.getLogger(__name__)


class UbersmithApi(models.TransientModel):
    _name = "ubersmith.api"
    _session = None

    def _get_session(self):
        if not self._session:
            self._session = requests.Session()
            settings = self.env['ubersmith.settings'].get()
            self._session.auth = (settings.username, settings.api_token)
        return self._session

    def _get(self, method, params=None):
        if not params:
            params = {}
        settings = self.env['ubersmith.settings'].get()
        url_endpoint = '%s?method=%s' % (settings.url, method)
        session = self.env.context.get('session', self._get_session())
        try:
            res = session.get(url_endpoint, params=params).json()
            data = res.get('data')
            if not res.get('status'):
                _logger.error('Ubersmith access error %d: %s',
                              res.get('error_code'), res.get('error_message'))
            return data if isinstance(data, dict) else {}
        except Exception, e:
            _logger.error("Cannot connect to Ubersmith API: %s", e)
            return {}

    def get_service_plans(self, brand_id):
        method = "uber.service_plan_list"
        settings = self.env['ubersmith.settings'].get()
        state = settings.get_service_plan_state()
        params = {
            'active': state,
            'brand_id': brand_id
        }
        return self._get(method, params)

    def get_service_plan(self, plan_id):
        method = "uber.service_plan_get"
        params = {
            'plan_id': plan_id
        }
        return self._get(method, params)

    def get_clients(self):
        method = "client.list"
        params = {'metadata[parent_account_id]': 1}
        return self._get(method, params)

    def get_brands(self):
        method = "uber.brand_list"
        params = {}
        return self._get(method, params)

    def get_client_services(self, client_id):
        method = "client.service_list"
        settings = self.env['ubersmith.settings'].get()
        state = settings.get_service_state()
        params = {'client_id': client_id,
                  'pack_type_select': state}
        return self._get(method, params)

    def get_client_invoices(self, client_id):
        method = "client.invoice_list"
        settings = self.env['ubersmith.settings'].get()
        state = settings.get_invoice_state()
        since = int(settings.invoice_generation_timestamp)
        params = {'client_id': client_id,
                  'paid': state,
                  'since': since}
        return self._get(method, params)

    def get_invoice(self, invoice_id):
        method = "client.invoice_get"
        params = {'invoice_id': invoice_id}
        return self._get(method, params)

    def get_tax_list(self, brand_id):
        method = "uber.tax_rate_list"
        params = {'brand_id': brand_id}
        return self._get(method, params)
