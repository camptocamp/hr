# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def po_auto_invoice(self):
        today = fields.Date.today()
        vendors = self.env['res.partner'].browse()
        invoice_ids = self.env['account.invoice'].browse()
        purchase_ids = self.env['purchase.order'].search(
            [('state', '=', 'purchase'),
             ('subscr_date_end', '>', today)])
        purchase_ids = self._check_po_in_invoice(purchase_ids)
        for purchase in purchase_ids:
            if purchase.partner_id.automatic_supplier_invoicing:
                vendors |= purchase.partner_id
        for vendor in vendors:
            if vendor.group_supplier_invoice:
                # Group all PO in one invoice
                inv = self.with_context(
                    journal_type='purchase', type='in_invoice').create(
                        {'partner_id': vendor.id, 'type': 'in_invoice'})
                for po in purchase_ids.filtered(
                        lambda r: r.partner_id == vendor):
                    inv.write({'purchase_id': po.id})
                    # Force the onchange trigger
                    inv.purchase_order_change()
                invoice_ids |= inv
            else:
                # Create one INV per PO
                for po in purchase_ids.filtered(
                        lambda r: r.partner_id == vendor):
                    inv = self.with_context(
                        journal_type='purchase', type='in_invoice').create(
                            {'partner_id': vendor.id, 'type': 'in_invoice'})
                    inv.write({'purchase_id': po.id})
                    # Force the onchange trigger
                    inv.purchase_order_change()
                    invoice_ids |= inv
            # Force computation of taxes
            invoice_ids.compute_taxes()
        return invoice_ids

    @api.model
    def _check_po_in_invoice(self, purchases):
        ''' The goal is to filter purchases which are already going to be
            invoiced.
        '''
        InvLine = self.env['account.invoice.line']
        for po in purchases:
            inv_lines = InvLine.search([('purchase_id', '=', po.id),
                                        ('invoice_id.state', '=', 'draft')])
            for line in inv_lines:
                purchases -= line.purchase_id
        return purchases
