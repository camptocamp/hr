# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json
import responses

from .common import BaseTestCase


class TestInvoice(BaseTestCase):

    @classmethod
    def setup_records(cls):
        cls.account = cls.env['account.account'].create({
            'name': 'Dummy account',
            'code': 'DUMMY',
            'user_type_id': cls.env.ref(
                'account.data_account_type_other_income').id
        })
        cls.invoice_model = cls.env['account.invoice']
        cls.invoice = cls.invoice_model.create({
            'partner_id': cls.env.ref('base.partner_demo').id,
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.env.ref('product.product_product_1').id,
                'price_unit': 1,
                'account_id': cls.account.id,
                'name': 'test'
            })]
        })

    @responses.activate
    def test_invoice_info(self):
        responses.add(
            responses.GET,
            self.ws._ws_url_for('invoice/info', self.invoice.id),
            body='',  # we don't know yet what the ws returns
            status=200,
            content_type='application/json',
        )
        self.ws.ws_get('invoice/info', {'id': self.invoice.id})
        self.assertEqual(1, len(responses.calls))
        request = responses.calls[0].request
        expected_body = {
            # TODO
            u"id": self.invoice.id,
        }
        self.assertEqual('application/json', request.headers['Content-Type'])
        self.assertDictEqual(expected_body, json.loads(request.body))

    @responses.activate
    def test_invoice_extralines(self):
        responses.add(
            responses.GET,
            self.ws._ws_url_for('invoice/extralines', self.invoice.id),
            body='',  # we don't know yet what the ws returns
            status=200,
            content_type='application/json',
        )
        self.ws.ws_get('invoice/extralines', {'id': self.invoice.id})
        self.assertEqual(1, len(responses.calls))
        request = responses.calls[0].request
        expected_body = {
            # TODO
            u"id": self.invoice.id,
        }
        self.assertEqual('application/json', request.headers['Content-Type'])
        self.assertDictEqual(expected_body, json.loads(request.body))
