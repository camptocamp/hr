# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.sale.tests import test_sale_common


class TestSaleMrpInvoicing(test_sale_common.TestSale):

    def setUp(self):
        super(TestSaleMrpInvoicing, self).setUp()

        self.p_uom_categ_1 = self.env['product.uom.categ'].create({
            'name': 'Bandwidth/time',
            'recurring': True
        })
        self.p_uom_1 = self.env['product.uom'].create({
            'name': 'Mpbs/month',
            'category_id': self.p_uom_categ_1.id,
        })

        self.so = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in self.products.iteritems()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        })

    def test_dummy(self):
        self.assertEquals(True, True)

    def test_contract_not_created_on_confirm_for_mrp(self):
        self.so.action_confirm()
        self.assertEquals(self.so.subscription_id, False)
