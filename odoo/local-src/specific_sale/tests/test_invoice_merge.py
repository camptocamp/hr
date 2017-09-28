# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase
import mock

INV_MOD = 'odoo.addons.specific_sale.models.account_invoice.AccountInvoice'


class TestInvoiceMerge(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInvoiceMerge, cls).setUpClass()
        cls.setup_records()

    @classmethod
    def setup_records(cls):
        cls.account = cls.env['account.account'].create({
            'name': 'Dummy account',
            'code': 'DUMMY',
            'user_type_id': cls.env.ref(
                'account.data_account_type_other_income').id
        })
        cls.account_analytic = \
            cls.env['account.analytic.account'].search([], limit=1)
        cls.invoice_model = cls.env['account.invoice']
        cls.default_line_values = {
            'product_id': cls.env.ref('product.product_product_1').id,
            'name': 'test',
            'price_unit': 1.0,
            'quantity': 1.0,
            'account_id': cls.account.id,
            'account_analytic_id': cls.account_analytic.id,
        }
        cls.invoice = cls.invoice_model.create({
            'partner_id': cls.env.ref('base.partner_demo').id,
            'invoice_line_ids': [(0, 0, cls.default_line_values)]
        })

    @mock.patch('%s._ws_get_extra_lines' % INV_MOD)
    def test_invoice_merge__no_extra_lines(self, _ws_get_extra_lines_mock):
        """No extra line from WS: invoice lines stay the same."""
        _ws_get_extra_lines_mock.return_value = []
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        self.invoice._ws_handle_extra_lines()
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)

    @mock.patch('%s._ws_get_extra_lines' % INV_MOD)
    def test_invoice_merge__add_extra_lines(self, _ws_get_extra_lines_mock):
        """Got extra line from WS: new invoice lines created."""
        prod = self.env.ref('product.product_product_2')
        _ws_get_extra_lines_mock.return_value = [{
            'product_id': prod.id,
            'name': prod.name,
            'quantity': 1.0,
            'price_unit': 10.0,
            'account_analytic_id': self.account_analytic.id,
            'account_id': self.account.id,
        }]
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        self.invoice._ws_handle_extra_lines()
        self.assertEqual(len(self.invoice.invoice_line_ids), 2)

    @mock.patch('%s._ws_get_info' % INV_MOD)
    def test_invoice_merge__validation(self, _ws_get_info):
        """Same lines from WS: order is validated automatically."""
        _ws_get_info.return_value = {
            'lines': [self.default_line_values, ]
        }
        self.assertEqual(self.invoice.state, 'draft')
        self.invoice._ws_handle_workflow()
        self.assertEqual(self.invoice.state, 'open')

    @mock.patch('%s._ws_get_info' % INV_MOD)
    def test_invoice_merge__no_validation(self, _ws_get_info):
        """Lines from WS do not match: order is NOT validated automatically."""
        vals = self.default_line_values.copy()
        vals['quantity'] = 2.0
        _ws_get_info.return_value = {
            'lines': [vals, ]
        }
        self.assertEqual(self.invoice.state, 'draft')
        self.invoice._ws_handle_workflow()
        self.assertEqual(self.invoice.state, 'draft')
