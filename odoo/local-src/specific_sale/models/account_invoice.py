# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for invoice in self:
            # TODO: can't we get this in 1 query?
            sale_orders = (invoice.invoice_line_ids.mapped('sale_line_ids')
                                                   .mapped('order_id'))
            for so in sale_orders:
                if so.all_mrc_delivered():
                    so.subscription_id = so.create_contract()
        return res

    # TODO 2017-10-11: webservice are not ready yet on customer side
    # @api.multi
    # def do_merge(self, keep_references=True, date_invoice=False,
    #              remove_empty_invoice_lines=True):
    #     res = super(AccountInvoice, self).do_merge(
    #         keep_references=keep_references, date_invoice=date_invoice,
    #         remove_empty_invoice_lines=remove_empty_invoice_lines)
    #     self._ws_handle_updates(res)
    #     return res

    def _ws_handle_updates(self, invoices):
        """Handle invoice updates via webservices."""
        for inv in self.browse(invoices.keys()):
            inv._ws_handle_extra_lines()
            inv._ws_handle_workflow()

    def _ws_get_extra_lines(self):
        """Retrieve extra invoce lines via WS."""
        ws = self.env['bso.ws']
        data = ws.ws_get('invoice/extralines', {'id': self.id})
        return data['lines']

    @api.multi
    def _ws_handle_extra_lines(self):
        """Update lines with extra lines if any."""
        self.ensure_one()
        newlines = []
        for line in self._ws_get_extra_lines():
            newlines.append((0, 0, self._extra_line_value(line)))
        if newlines:
            self.write({'invoice_line_ids': newlines})

    def _extra_line_value(self, line):
        """Convert WS line to INV line values."""
        values = {}
        # TODO: what do we really get from extra lines endpoint?
        # ATM we assume we get real odoo values
        values.update(line)
        return values

    def _ws_get_info(self):
        """Call WS to get info on current invoice."""
        ws = self.env['bso.ws']
        return ws.ws_get('invoice/info', {'id': self.id})

    @api.multi
    def _ws_handle_workflow(self):
        """Apply workflow changes based on WS info."""
        self.ensure_one()
        info = self._ws_get_info()
        if self._ws_check_line_match(info['lines']):
            # we can validate it
            self.action_invoice_open()
            self.partner_auto_send()

    def _ws_check_line_match(self, ws_lines):
        """Verify if WS lines match current INV lines."""
        if len(ws_lines) != len(self.invoice_line_ids):
            return False
        match_fields = (
            'product_id',  # required
            'account_analytic_id', 'quantity', 'price_unit')
        # group lines by product
        # TODO: can we have more than one line per product?
        inv_grouped = {
            x['product_id']: x
            for x in self.invoice_line_ids.read(
                match_fields, load='_classic_write')
        }
        ws_grouped = {x['product_id']: x for x in ws_lines}
        for product_id, inv_line in inv_grouped.iteritems():
            ws_line = ws_grouped.get(product_id)
            if not ws_line:
                return False
            # TODO: anything else to check?
            for k in match_fields:
                if inv_line[k] != ws_line.get(k):
                    return False
        return True

    def partner_auto_send(self):
        """Send mail to invoiced partner."""
        pass

    def _partner_send_email(self):
        """Send email in any case."""
        action = self.action_invoice_sent()
        ctx = action['context']
        composer = \
            self.env['mail.compose.message'].with_context(**ctx).create()
        composer.send_mail(auto_commit=True)

    def _partner_send_snail(self):
        """Print it."""
        report = self.env.ref('account.account_invoices')
        # this takes care of printing it too
        report.get_pdf()
