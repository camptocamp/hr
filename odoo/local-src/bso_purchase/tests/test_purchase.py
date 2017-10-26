# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from . import common
from odoo import fields
from dateutil.relativedelta import relativedelta


class TestPurchase(common.TestBsoPurchaseCommon):

    def test_create_update_qty(self):
        self.po.button_confirm()
        self.assertEqual(self.po.state, 'purchase')
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        self.assertEqual(10.0, picking.move_lines.product_uom_qty)

    def test_auto_invoicing_group(self):
        self.partner_id.write({
            'group_supplier_invoice': True,
            'automatic_supplier_invoicing': True,
        })
        self.po.button_confirm()
        self.po2.button_confirm()
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        picking2 = self.po2.picking_ids[0]
        picking2.do_transfer()

        # There should be zero invoices as no end date for subscr
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))
        # if we do it twice there should be no new invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))

    def test_auto_invoicing_no_group(self):
        self.partner_id.write({
            'group_supplier_invoice': False,
            'automatic_supplier_invoicing': True,
        })
        # Prepare the PO to be invoiced
        self.po.button_confirm()
        self.po2.button_confirm()
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        picking2 = self.po2.picking_ids[0]
        picking2.do_transfer()

        # There should be zero invoices as no end date for subscr
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))

        # There should be no new invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))

    def test_auto_invoicing_group_end_date(self):
        self.partner_id.write({
            'group_supplier_invoice': True,
            'automatic_supplier_invoicing': True,
        })
        self.po.button_confirm()
        self.po2.button_confirm()
        today_date = fields.Date.from_string(fields.Date.today())
        end = today_date + relativedelta(months=3)
        self.po.subscr_date_end = end
        self.po2.subscr_date_end = end
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        picking2 = self.po2.picking_ids[0]
        picking2.do_transfer()

        # There should be 1 invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(1, len(inv_ids))
        # if we do it twice there should be no new invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))

    def test_auto_invoicing_no_group_end_date(self):
        self.partner_id.write({
            'group_supplier_invoice': False,
            'automatic_supplier_invoicing': True,
        })
        # Prepare the PO to be invoiced
        self.po.button_confirm()
        self.po2.button_confirm()
        today_date = fields.Date.from_string(fields.Date.today())
        end = today_date + relativedelta(months=3)
        self.po.subscr_date_end = end
        self.po2.subscr_date_end = end
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        picking2 = self.po2.picking_ids[0]
        picking2.do_transfer()

        # There should be 2 invoices
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(2, len(inv_ids))

        # There should be no new invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))
