# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.addons.sale.tests.test_sale_common import TestSale

MINIMAL_B64 = 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA='


class TestSaleTasks(TestSale):

    def setUp(self):
        super(TestSaleTasks, self).setUp()
        self.partner.ref = 'XYZ'

    def test_sale_service(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'project')])
        next_sequence_number = sequence.number_next_actual

        product = self.env['product.product'].create({
            'name': 'Test',
            'type': 'service',
            'track_service': 'task',
        })
        zone = self.env['project.zone'].create({'code': 'A', 'name': 'A'})
        process = self.env['project.process'].create(
            {'code': 'B', 'name': 'B'}
        )
        market = self.env['project.market'].create({'code': 'C', 'name': 'C'})
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {'name': product.name,
                        'product_id': product.id,
                        'product_uom_qty': 50,
                        'product_uom': product.uom_id.id,
                        'price_unit': 100.})],
            'pricelist_id': self.env.ref('product.list0').id,
            'project_zone_id': zone.id,
            'project_process_id': process.id,
            'project_market_id': market.id,
            'sales_condition': MINIMAL_B64,
            'sales_condition_filename': 'dummy.pdf',
        }
        so = self.env['sale.order'].create(so_vals)
        so.action_validate_eng()
        so.action_validate_sys()
        so.action_validate_pro()
        so.action_confirm()
        self.assertEqual(so.state, 'final_quote')
        so.action_confirm()
        self.assertEqual(so.state, 'sale')

        analytic_account = so.project_id
        expected_code = str(next_sequence_number).zfill(3) + 'ABCABC'
        self.assertEqual(expected_code, analytic_account.name)

        task = analytic_account.project_ids.task_ids
        expected_task_name = "%s:%s" % (expected_code, product.name)
        self.assertEqual(expected_task_name, task.name)
