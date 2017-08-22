# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from . import common


class TestPurchase(common.TestBsoPurchaseCommon):

    def test_create_update_qty(self):
        self.po.button_confirm()
        self.assertEqual(self.po.state, 'purchase')
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        # As we don't provide reference_date, move_date = ref_date =date.today
        # and qty = 0.0
        self.assertEqual(10.0, picking.move_lines.product_uom_qty)

        # self.po.
        # We should have a stock move with delivered qty = 10.0
        # self.assertEqual(10.0, self.po.order_line.qty_received)

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

        # There should be only one invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(1, len(inv_ids))
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

        # There should be two invoices
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(2, len(inv_ids))

        # There should be no new invoice
        inv_ids = self.AccountInvoice.po_auto_invoice()
        self.assertEqual(0, len(inv_ids))
