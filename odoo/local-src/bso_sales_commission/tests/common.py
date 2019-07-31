# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):
    def setUp(self):
        super(TestCommon, self).setUp()
        self.original_salesperson = self._create_user('original_salesperson')
        self.extra_salesperson1 = self._create_user('extra_salesperson1')
        self.extra_salesperson2 = self._create_user('extra_salesperson2')
        self.so = self._create_so()
        self.so_copy = self._create_so()
        self.original_salesperson_target = self._create_target()

    def _create_user(self, name):
        group_user = self.env.ref('sales_team.group_sale_salesman')
        return self.env['res.users'].create({
            'name': name,
            'login': name,
            'email': '%s@example.com' % name,
            'groups_id': [(6, 0, [group_user.id])],
            'employee_ids': [(0, 0, {'name': name})]

        })

    def _create_so(self):
        partner = self.env.ref('base.partner_root')
        partner.write({'ref': 'ref123'})
        nrr_product = self._create_nrr_product()
        mrr_product = self._create_mrr_product()
        so = self.env['sale.order'].create({
            'partner_id': partner.id,
            'user_id': self.original_salesperson.id,
            'currency_id': self.env.ref('base.EUR').id,
            'duration': 12,
            'order_line':
                [(0, 0, {
                    'name': nrr_product.name,
                    'product_id': nrr_product.id,
                    'product_uom_qty': 1,
                    'product_uom': nrr_product.uom_id.id,
                    'price_unit': 12500
                }),
                 (0, 0, {
                     'name': mrr_product.name,
                     'product_id': mrr_product.id,
                     'product_uom_qty': 1,
                     'product_uom': mrr_product.uom_id.id,
                     'price_unit': 8333.3

                 })]
        })

        return so

    def _create_nrr_product(self):
        return self.env['product.product'].create({
            'name': 'NRR Product',
            'type': 'product',
            'standard_price': 10000,
        })

    def _create_mrr_product(self):
        categ_id = self.env['product.uom.categ'].create(
            {'name': 'Unit/time',
             'recurring': True})
        uom_id = self.env['product.uom'].create({
            'name': 'Unit/month',
            'recurring': True,
            'factor_inv': 10,
            'uom_type': 'bigger',
            'rounding': 1.0,
            'category_id': categ_id.id,
        })
        return self.env['product.product'].create({
            'name': 'MRR Product',
            'type': 'product',
            'standard_price': 5000,
            'recurring_invoice': True,
            'uom_id': uom_id.id,
            'uom_po_id': uom_id.id,
            'invoice_policy': 'delivery',
        })

    def _assert_salespeople(self, expected_salespeople):
        so = self.so
        commission_lines = so.salesperson_commission_line_ids
        salespeople = commission_lines.mapped('user_id')
        self.assertEqual(salespeople, expected_salespeople)

    def _assert_total_percentages_is_100(self):
        so = self.so
        commission_lines = so.salesperson_commission_line_ids
        sum_percentages = sum(commission_lines.mapped('percentage'))
        self.assertEqual(sum_percentages, 100)

    def _create_target(self):
        return self.env['sale.target'].create({
            'user_id': self.original_salesperson.id,
            'year': datetime.now().year,
            'currency_id': self.env.ref('base.EUR').id,
            'annual_target_nrr': 144000,
            'annual_target_mrr': 108000,
        })

    @staticmethod
    def _create_dealsheet_and_confirm(so):
        so.action_dealsheet()
        so.dealsheet_id.action_confirm()
        so.action_confirm()
        return so
