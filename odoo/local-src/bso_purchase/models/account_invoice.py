# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def po_auto_invoice(self, interval):
        today = fields.Date.today()
        vendors = self.env['res.partner'].browse()
        invoice_ids = self.env['account.invoice'].browse()
        purchase_ids = self.env['purchase.order'].search(
            [('state', '=', 'purchase'),
             ('subscr_date_end', '>', today)])
        data_dict = {}
        purchase_ids = self._check_po_in_invoice(purchase_ids)
        for purchase in purchase_ids:

            company = purchase.company_id

            if purchase.partner_id.automatic_supplier_invoicing:
                vendors |= purchase.partner_id
            if company not in data_dict:
                data_dict[company] = {
                    purchase.partner_id: {purchase.currency_id: [purchase]}}
            else:
                if purchase.partner_id not in data_dict[company]:
                    data_dict[company][purchase.partner_id] = {
                        purchase.currency_id: [purchase]}
                else:
                    dcp = data_dict[company][purchase.partner_id]
                    if purchase.currency_id not in dcp:
                        dcp[purchase.currency_id] = [purchase]
                    else:
                        dcp[purchase.currency_id].append(purchase)

        for vendor in vendors:
            if vendor.group_supplier_invoice:
                for comp, vendor_dict in data_dict.iteritems():
                    if vendor in vendor_dict:
                        for curr, po_list in vendor_dict[vendor].iteritems():
                            # Group all PO in one invoice
                            inv = self.with_context(
                                force_company=comp.id,
                                default_company_id=comp.id,
                                journal_type='purchase',
                                type='in_invoice').create(
                                    {'partner_id': vendor.id,
                                     'type': 'in_invoice'})
                            inv._onchange_partner_id()
                            inv.currency_id = curr.id
                            for po in po_list:
                                inv.write({'purchase_id': po.id})
                                # Force the onchange trigger
                                inv.purchase_order_change()
                            invoice_ids |= inv
            else:
                # Create one INV per PO
                for po in purchase_ids.filtered(
                        lambda r: r.partner_id == vendor):
                    inv = self.with_context(
                        force_company=po.company_id.id,
                        default_company_id=po.company_id.id,
                        journal_type='purchase', type='in_invoice').create(
                            {'partner_id': vendor.id, 'type': 'in_invoice'})
                    inv._onchange_partner_id()
                    inv.currency_id = po.currency_id.id
                    inv.write({'purchase_id': po.id})
                    # Force the onchange trigger
                    inv.purchase_order_change()
                    invoice_ids |= inv
            # Force computation of taxes
            invoice_ids.compute_taxes()

        # write start_date and end_date on created invoices
        for line in invoice_ids.mapped('invoice_line_ids'):
            line.write(line.update_dates(today, interval=interval))
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
