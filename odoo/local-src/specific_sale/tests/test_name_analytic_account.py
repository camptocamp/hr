# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from __future__ import division
from .common import BaseCase


class TestNameAnalyticAccount(BaseCase):

    @classmethod
    def setup_records(self):
        self.product_template = self.env['product.template'].create({
            'name': 'Product',
        })
        self.product_product = self.product_template.product_variant_ids[0]
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
        self.sol_1 = self.env['sale.order.line'].create({
            'order_id': self.so.id,
            'name': self.product_product.name,
            'product_id': self.product_product.id,
            'product_uom_qty': 3,
            'product_uom': self.product_product.uom_id.id,
        })
        sequence = self.env.ref(
            'specific_sale.seq_end_name_account_analytic_account'
        )
        sequence.number_next_actual = 1

    def test_name_analytic_account_1(self):
        """ Test analytic account name 1 (from sale order)"""
        self.so.action_confirm()
        account_analytic_name = self.so.project_id.name
        self.assertEquals(account_analytic_name, 'FR101/12345/000001')

    def test_name_analytic_account_2(self):
        """ Test analytic account name 2 (manually created) """
        account_analytic = self.env['account.analytic.account'].create({
            'name': 'test_with_name',
        })
        account_analytic_name = account_analytic.name
        self.assertEquals(account_analytic_name, 'test_with_name')
