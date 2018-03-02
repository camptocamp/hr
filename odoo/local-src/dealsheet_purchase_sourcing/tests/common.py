# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests.common as common
from collections import defaultdict


class BaseTestCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.wiz_model = cls.env['wiz.sale.dealsheet.source']
        cls.sale_order_model = cls.env['sale.order'].with_context(
            tracking_disable=1)
        cls.dealsheet_model = cls.env['sale.dealsheet'].with_context(
            tracking_disable=1)
        cls.user_model = cls.env['res.users'].with_context({
            'tracking_disable': True,
            'no_reset_password': True,
            'mail_create_nosubscribe': True
        })
        cls.prod_iPadMini = cls.env.ref('product.product_product_6')
        cls.prod_iMac = cls.env.ref('product.product_product_8')
        cls.prod_appleWLKB = cls.env.ref('product.product_product_9')
        cls.prod_gcard = cls.env.ref('product.product_product_24')
        cls.uom_unit = cls.env.ref('product.product_uom_unit')
        cls.uom_unit_month = cls.env.ref('specific_product.product_unit_month')
        cls.prod_tmpl_rec = cls.env['product.template'].create({
            'name': 'Recurring product',
            'type': 'product',
            'recurring_invoice': True,
            'invoice_policy': 'delivery',
            'uom_id': cls.uom_unit_month.id,
            'uom_po_id': cls.uom_unit_month.id,
            'price': 20.0,
        })
        cls.prod_rec = cls.env['product.product'].create({
            'product_tmpl_id': cls.prod_tmpl_rec.id,
        })
        cls.partner = cls.env.ref('base.res_partner_4')
        cls.setup_dealsheet()
        cls.load_suppliers()

    @classmethod
    def setup_dealsheet(cls):
        sol1_vals = {
            'product_id': cls.prod_iPadMini.id,
            'name': "iPad Mini",
            'product_uom': cls.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': cls.prod_iPadMini.lst_price
        }
        sol2_vals = {
            'product_id': cls.prod_iMac.id,
            'name': "iMac",
            'product_uom': cls.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': cls.prod_iMac.lst_price
        }
        sol3_vals = {
            'product_id': cls.prod_appleWLKB.id,
            'name': "iMac",
            'product_uom': cls.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': cls.prod_appleWLKB.lst_price
        }
        sol4_vals = {
            'product_id': cls.prod_gcard.id,
            'name': "iMac",
            'product_uom': cls.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': cls.prod_gcard.lst_price
        }
        sol5_vals = {
            'product_id': cls.prod_rec.id,
            'name': "Test rec",
            'product_uom': cls.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': cls.prod_rec.lst_price
        }
        so_vals = {
            'partner_id': cls.partner.id,
            'order_line': [
                (0, None, sol1_vals),
                (0, None, sol2_vals),
                (0, None, sol3_vals),
                (0, None, sol4_vals),
                (0, None, sol5_vals),
            ]
        }
        cls.sale_order = cls.sale_order_model.create(so_vals)
        cls.dealsheet = cls.sale_order.dealsheet_create()
        cls.sale_manager = cls.user_model.create({
            'name': 'Test Sale Manager',
            'login': 'test_sale_manager',
            'email': 'test_sale_manager@example.com',
            'groups_id': [
                (4, cls.env.ref('sales_team.group_sale_manager').id),
                (4, cls.env.ref('purchase.group_purchase_manager').id),
                (4, cls.env.ref('bso_backbone.bso_ops_confidential').id),
            ]
        })

    @classmethod
    def load_suppliers(cls):
        cls.prods = [
            cls.prod_appleWLKB, cls.prod_iPadMini,
            cls.prod_iMac, cls.prod_gcard, cls.prod_rec
        ]
        # at 1st load we should get all the suppliers for missing sources
        cls.all_suppliers = cls.env['res.partner'].browse()
        cls.prod_suppliers = defaultdict(cls.env['res.partner'].browse)
        for prod in cls.prods:
            suppls = prod.seller_ids.mapped('name')
            cls.all_suppliers += suppls
            cls.prod_suppliers[prod.id] += suppls
