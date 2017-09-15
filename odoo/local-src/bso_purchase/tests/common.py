# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime
from dateutil import relativedelta

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import odoo.tests.common as common


class TestBsoPurchaseCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBsoPurchaseCommon, cls).setUpClass()

        # Useful models
        cls.PurchaseOrder = cls.env['purchase.order']
        cls.PurchaseOrderLine = cls.env['purchase.order.line']
        cls.AccountInvoice = cls.env['account.invoice']
        cls.AccountInvoiceLine = cls.env['account.invoice.line']
        # Create uom and uom category with recurring invoicing
        cls.p_uom_categ_recurring = cls.env['product.uom.categ'].create({
            'name': 'Unit/time',
            'recurring': True
        })
        cls.p_uom_1 = cls.env['product.uom'].create({
            'name': 'Unit/month',
            'category_id': cls.p_uom_categ_recurring.id,
        })
        # Create uom and uom category without recurring invoicing
        cls.p_uom_categ_non_recurring = cls.env['product.uom.categ'].create({
            'name': 'Unit',
            'recurring': False
        })
        cls.p_uom_2 = cls.env['product.uom'].create({
            'name': 'Unit/month',
            'category_id': cls.p_uom_categ_non_recurring.id,
        })
        # Create a MRC product
        cls.prod_tmpl_rent_server = cls.env['product.template'].create({
            'name': 'Rent server',
            'uom_id': cls.p_uom_1.id,
            'uom_po_id': cls.p_uom_1.id,
            'list_price': 30,
            'recurring_invoice': True,
            'invoice_policy': 'delivery'
        })
        cls.prod_rent_server = cls.env['product.product'].create({
            'product_tmpl_id': cls.prod_tmpl_rent_server.id,
        })
        # Create a NRC product
        cls.prod_tmpl_setup_server = cls.env['product.template'].create({
            'name': 'Set up server',
            'uom_id': cls.p_uom_2.id,
            'uom_po_id': cls.p_uom_2.id,
            'list_price': 100,
            'recurring_invoice': False,
            'invoice_policy': 'order'
        })
        cls.prod_setup_server = cls.env['product.product'].create({
            'product_tmpl_id': cls.prod_tmpl_setup_server.id,
        })
        # Get a vendor
        cls.partner_id = cls.env.ref('base.res_partner_4')
        # Create a purchase with MRC Product
        subcr_date = datetime.now() + relativedelta.relativedelta(months=+1)
        po_vals = {
            'partner_id': cls.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': cls.prod_rent_server.name,
                    'product_id': cls.prod_rent_server.id,
                    'product_qty': 10,
                    'product_uom': cls.prod_rent_server.uom_po_id.id,
                    'price_unit': 30,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ],
            'subscr_date_end': subcr_date,
        }
        cls.po = cls.PurchaseOrder.create(po_vals)
        po_vals2 = {
            'partner_id': cls.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': cls.prod_rent_server.name,
                    'product_id': cls.prod_rent_server.id,
                    'product_qty': 10,
                    'product_uom': cls.prod_rent_server.uom_po_id.id,
                    'price_unit': 30,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ],
            'subscr_date_end': subcr_date,
        }
        cls.po2 = cls.PurchaseOrder.create(po_vals2)
