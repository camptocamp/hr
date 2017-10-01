# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from __future__ import division
from odoo.addons.sale.tests import test_sale_common


class TestSaleMrpInvoicing(test_sale_common.TestSale):

    def setUp(self):
        super(TestSaleMrpInvoicing, self).setUp()
        Contract = self.env['sale.subscription']

        self.p_uom_categ_recurring = self.env['product.uom.categ'].create({
            'name': 'Unit/time',
            'recurring': True
        })
        self.p_uom_1 = self.env['product.uom'].create({
            'name': 'Unit/month',
            'category_id': self.p_uom_categ_recurring.id,
        })
        # Create uom and uom category without recurring invoicing
        self.p_uom_categ_non_recurring = self.env['product.uom.categ'].create({
            'name': 'Unit',
            'recurring': False
        })
        self.p_uom_2 = self.env['product.uom'].create({
            'name': 'Unit/month',
            'category_id': self.p_uom_categ_non_recurring.id,
        })
        # Create a MRC product
        self.prod_tmpl_rent_server = self.env['product.template'].create({
            'name': 'Rent server',
            'uom_id': self.p_uom_1.id,
            'uom_po_id': self.p_uom_1.id,
            'list_price': 30,
            'recurring_invoice': True,
            'invoice_policy': 'delivery'
        })
        self.prod_rent_server = self.env['product.product'].create({
            'product_tmpl_id': self.prod_tmpl_rent_server.id,
        })
        # Create a NRC product
        self.prod_tmpl_setup_server = self.env['product.template'].create({
            'name': 'Set up server',
            'uom_id': self.p_uom_2.id,
            'uom_po_id': self.p_uom_2.id,
            'list_price': 100,
            'recurring_invoice': False,
            'invoice_policy': 'order'
        })
        self.prod_setup_server = self.env['product.product'].create({
            'product_tmpl_id': self.prod_tmpl_setup_server.id,
        })
        # ubscription template
        self.sbscription_tmpl = self.env['sale.subscription.template'].create(
            {
                'name': 'Special subscription',
                'subscription_template_line_ids': [(0, 0, {
                    'product_id': self.prod_rent_server.id,
                    'name': 'Recurring template line',
                    'uom_id': self.prod_rent_server.uom_id.id})]
            })
        # Create a sale order with the two previous products
        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'contract_template': self.sbscription_tmpl.id,
            'order_line': [
            ]
        })
        self.sol_1 = self.env['sale.order.line'].create({
            'order_id': self.so.id,
            'name': self.prod_rent_server.name,
            'product_id': self.prod_rent_server.id,
            'product_uom_qty': 3,
            'product_uom': self.p_uom_1.id,
            'price_unit': self.prod_rent_server.list_price
        })
        self.sol_2 = self.env['sale.order.line'].create({
            'order_id': self.so.id,
            'name': self.prod_setup_server.name,
            'product_id': self.prod_setup_server.id,
            'product_uom_qty': 3,
            'product_uom': self.p_uom_2.id,
            'price_unit': self.prod_setup_server.list_price
        })

        self.contract = Contract.create({
            'name': 'TestContract',
            'state': 'open',
            'pricelist_id': self.ref('product.list0'),
            'template_id': self.sbscription_tmpl.id,
        })
        self.contract.on_change_template()

    def test_recurring_value_uom(self):
        """ Test that recurring value is passed along """
        self.assertEquals(self.p_uom_1.recurring,
                          self.p_uom_categ_recurring.recurring)

    def test_full_processus(self):
        """ Test sale order with one MRC product and one NRC product
            with multiple delivery and invoices at specific dates
        """
        # Confirm the sale order
        self.so.create_date = "2017-06-1 12:00:00"
        self.so.action_confirm()
        self.so.date_order = "2017-06-1 12:00:00"
        self.assertEquals(self.so.subscription_id.id, False, '')
        # Make a partial delivery of 1 for both product on june 10th
        pick = self.so.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({'qty_done': 1})
        wiz_act = pick.do_new_transfer()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.process()
        pick.pack_operation_product_ids.write({
            'date': '2017-06-10 12:00:00',
            'create_date': '2017-06-10 12:00:00'})
        moves = pick.move_lines
        moves.write({
            'date': '2017-06-10 12:00:00',
            'create_date': '2017-06-10 12:00:00'
        })
        # Checking the delivered quantity after first delivery
        self.assertEquals(self.sol_1.qty_delivered, 0,
                          'There should be no qty_deliverd for MRC')
        self.assertEquals(self.sol_2.qty_delivered, 1,
                          'There should be a qty_delivered of one for NRC')
        # Check the qty_delivered on 1st of July
        # 21 days out of 30 for that month
        self.env.context = {
                'ref_date_mrc_delivery': '2017-07-01 12:00:00'
            }
        delivered_qty = (30 - (10 - 1)) / 30
        self.assertAlmostEquals(
                self.sol_1._get_delivered_qty(), delivered_qty, 3,
                'Delivered quantity on 1st July for the MRC is not correct')
        # Generate invoice using action for another date 1st July
        # First wizard, to select the reference date for MRC products
        wiz_act = self.so.action_invoicing()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.ref_date = '2017-07-01 12:00:00'
        self.env.context = {
            'active_id': self.so.id,
            'active_ids': [self.so.id]
        }
        wiz_act = wiz.button_ok()
        # Second wizard, that generate the invoice
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.advance_payment_method = 'delivered'
        wiz.create_invoices()
        self.assertEquals(len(self.so.invoice_ids), 1,
                          'Only one invoice should have been created')
        invoice_line = self.so.invoice_ids[0].invoice_line_ids
        self.assertAlmostEquals(invoice_line[0].quantity, delivered_qty, 3,
                                'The invoiced quantity in June for the '
                                'subscription is incorrect')
        self.assertEquals(invoice_line[1].quantity, 3,
                          'The invoiced quantity for the server is not 3')

        # Delivery of the two last server on the 20th of July
        pick = self.so.picking_ids.filtered(
                lambda r: r.state not in ['done', 'cancelled'])
        pick.force_assign()
        wiz_act = pick.do_new_transfer()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.process()
        pick.pack_operation_product_ids.write({
            'date': '2017-07-20 12:00:00',
            'create_date': '2017-07-20 12:00:00'})
        moves = pick.move_lines
        moves.write({
            'date': '2017-07-20 12:00:00',
            'create_date': '2017-07-20 12:00:00'
        })
        self.env.context = {
                'ref_date_mrc_delivery': '2017-08-01 12:00:00'
            }
        # Checking the delivered qty for the MRC product
        delivered_qty += 1
        delivered_qty += (12 / 31) * 2
        self.assertAlmostEquals(
                self.sol_1._get_delivered_qty(),
                delivered_qty, 3,
                'The delivered quantity for MRC on 1st August is not correct')
        # Generate the 2nd invoice
        wiz_act = self.so.action_invoicing()
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.ref_date = '2017-08-01 12:00:00'
        self.env.context = {
            'active_id': self.so.id,
            'active_ids': [self.so.id]
        }
        wiz_act = wiz.button_ok()
        # Second wizard, that generate the invoice
        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
        wiz.advance_payment_method = 'delivered'
        wiz.create_invoices()
        self.assertEquals(len(self.so.invoice_ids), 2,
                          'There should be two invoices created')
        invoice_line = self.so.invoice_ids[0].invoice_line_ids
        invoiced_qty = 1 + 2 * (12/31)
        self.assertAlmostEquals(invoice_line[0].quantity, invoiced_qty, 3,
                                'The invoiced quantity for the subscription'
                                'on 1st August is incorrect')
        self.assertEquals(len(invoice_line), 1,
                          'The 2nd invoice should have only one line')
        self.assertIsNot(len(self.so.subscription_id), 0,
                         'The subscription should be created when the '
                         'sale order is completely invoiced')
        date_invoice = self.so.invoice_ids[0].create_date.split(' ')[0]
        self.assertEquals(date_invoice,
                          self.so.subscription_id.date_start,
                          'The start date of the subscription should '
                          'be equal to the creation date of the last'
                          'invoice generated')

    def test_create_invoice(self):
        self.contract.write({'template_id': self.sbscription_tmpl.id})
        self.contract.on_change_template()
        self.contract._compute_recurring_total()

        invoice = self.contract._recurring_create_invoice()[0]
        self.contract.action_subscription_invoice()
        self.assertNotEqual(0.0, invoice.amount_total)
