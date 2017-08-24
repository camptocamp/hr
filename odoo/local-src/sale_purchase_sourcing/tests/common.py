# -*- coding: utf-8 -*-
# Author: Simone Orsi
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from collections import defaultdict


class BaseTestCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.wiz_model = cls.env['wiz.sale.order.source']
        cls.so_model = cls.env['sale.order']
        cls.prod_iPadMini = cls.env.ref('product.product_product_6')
        cls.prod_iMac = cls.env.ref('product.product_product_8')
        cls.prod_appleWLKB = cls.env.ref('product.product_product_9')
        cls.prod_gcard = cls.env.ref('product.product_product_24')
        cls.uom_unit = cls.env.ref('product.product_uom_unit')
        cls.partner = cls.env.ref('base.res_partner_4')
        cls.setup_order()
        cls.load_suppliers()

    @classmethod
    def setup_order(cls):
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
        so_vals = {
            'partner_id': cls.partner.id,
            'order_line': [
                (0, None, sol1_vals),
                (0, None, sol2_vals),
                (0, None, sol3_vals),
                (0, None, sol4_vals),
            ]
        }
        cls.sale_order = cls.so_model.create(so_vals)

    @classmethod
    def load_suppliers(cls):
        cls.prods = [
            cls.prod_appleWLKB, cls.prod_iPadMini,
            cls.prod_iMac, cls.prod_gcard,
        ]
        # at 1st load we should get all the suppliers for missing sources
        cls.all_suppliers = cls.env['res.partner'].browse()
        cls.prod_suppliers = defaultdict(cls.env['res.partner'].browse)
        for prod in cls.prods:
            suppls = prod.seller_ids.mapped('name')
            cls.all_suppliers += suppls
            cls.prod_suppliers[prod.id] += suppls
