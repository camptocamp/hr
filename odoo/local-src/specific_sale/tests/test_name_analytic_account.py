# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from __future__ import division
from .common import BaseCase


class TestNameAnalyticAccount(BaseCase):

    @classmethod
    def setup_records(cls):
        cls.product_product = cls.env['product.product'].create({
            'name': 'Product',
        })

    @classmethod
    def create_so(cls, partner):
        so = cls.env['sale.order'].create({
            'partner_id': partner.id,
        })
        cls.env['sale.order.line'].create({
            'order_id': so.id,
            'name': cls.product_product.name,
            'product_id': cls.product_product.id,
            'product_uom_qty': 3,
            'product_uom': cls.product_product.uom_id.id,
        })
        return so

    def test_name_analytic_account_1(self):
        """ Test analytic account name 1 (from sale order)"""
        self.env['ir.sequence'].search(
            [('code', 'like', 'analytic.account.name.%')]
        ).unlink()
        so = self.create_so(self.partner)
        so2 = self.create_so(self.partner)
        so3 = self.create_so(self.partner2)
        so.action_confirm()
        so2.action_confirm()
        so3.action_confirm()
        self.assertEquals(so.project_id.name, 'FR101/12345/000001')
        self.assertEquals(so2.project_id.name, 'FR101/12345/000002')
        self.assertEquals(so3.project_id.name, 'FR101/34567/000001')

    def test_name_analytic_account_2(self):
        """ Test analytic account name 2 (manually created) """
        account_analytic = self.env['account.analytic.account'].create({
            'name': 'test_with_name',
        })
        account_analytic_name = account_analytic.name
        self.assertEquals(account_analytic_name, 'test_with_name')
