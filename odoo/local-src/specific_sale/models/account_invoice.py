# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta
from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        rec = super(AccountInvoice, self).create(vals)
        if rec.type.startswith('out_'):
            # partner is the commercial entity
            # -> subscribe all the contacts with partner_type = 'invoice'
            # to the invoice (BSIBSO-1047)
            partner = rec.partner_id
            company_partner = partner.commercial_partner_id
            rec.partner_id = company_partner
            contacts = company_partner.child_ids.filtered(
                lambda r: r.type == 'invoice'
            )
            rec = rec.with_context(mail_auto_subscribe_no_notify=1)
            rec.message_unsubscribe(partner_ids=partner.ids)
            rec.message_subscribe(partner_ids=company_partner.ids)
            if contacts:
                rec.message_subscribe(partner_ids=contacts.ids)
                rec.message_unsubscribe(partner_ids=partner.ids)
        return rec

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

    @api.multi
    def action_invoice_sent(self):
        """Override to handle partner settings.

        When the composer wizard is opened the PDF is produced.
        When this happens the report tries to print it as well
        if the action type is set to `server` (as we did).
        To skip printing we use the proper flag in the context.
        """
        action = super(AccountInvoice, self).action_invoice_sent()
        partner = self.partner_id
        if partner.invoice_send_method not in ('snail', 'both'):
            # set flag to skip printing
            # See `base_report_to_printer.models.report.Report_can_print_report`  # noqa
            action['context']['must_skip_send_to_printer'] = True
        return action

    def partner_auto_send(self):
        """Send mail to invoiced partner."""
        if self.env.context.get('ws_invoice_skip_auto_send'):
            return
        if not self.partner_id.invoice_send_method:
            return
        if self.partner_id.invoice_send_method in ('snail', 'both'):
            self._partner_send_snail()
        if self.partner_id.invoice_send_method in ('both', 'email'):
            self._partner_send_email()

    def _partner_send_email(self):
        """Send email in any case."""
        action = self.action_invoice_sent()
        ctx = action['context']
        composer = \
            self.env['mail.compose.message'].with_context(**ctx).create({})
        composer.send_mail(auto_commit=True)

    def _partner_send_snail(self):
        """Print it."""
        report = self.env.ref('account.account_invoices')
        # this takes care of printing it too
        report.get_pdf()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def _set_additional_fields(self, invoice):
        if self.product_id.recurring_invoice and \
                not self.start_date and not self.end_date:
            # test_today is used in tests to force a date
            today = self.env.context.get('test_today',
                                         fields.Date.today())
            date_dict = self.update_dates(today)
            if 'ref_date_mrc_delivery' in self.env.context:
                refdatetime = fields.Datetime.from_string(
                    self.env.context['ref_date_mrc_delivery']
                )
                # end date is the day before the ref_date
                refdate = fields.Date.to_string(
                    refdatetime.date() - timedelta(days=1)
                )
                date_dict['start_date'] = today
                date_dict['end_date'] = refdate

            self.write(date_dict)

        super(AccountInvoiceLine, self)._set_additional_fields(invoice)

    @api.model
    def create(self, values):
        res = super(AccountInvoiceLine, self).create(values)
        if res.origin and res.origin not in res.name:
            res.name = u"{},\n{}".format(res.origin, res.name)
        return res

    @api.multi
    def write(self, values):
        res = super(AccountInvoiceLine, self).write(values)
        for line in self:
            if line.origin and line.origin not in line.name:
                line.name = u"{},\n{}".format(line.origin, line.name)
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.invoice.tax"

    amount_currency = fields.Monetary('Amount (company currency)',
                                      currency_field='company_currency_id',
                                      compute='_compute_amount_currency')
    company_currency_id = fields.Many2one(related='company_id.currency_id')
    exchange_rate = fields.Float('Exchange rate',
                                 compute='_compute_exchange_rate')

    @api.depends('invoice_id.date', 'currency_id', 'company_currency_id')
    def _compute_exchange_rate(self):
        for rec in self:
            date = rec.invoice_id.date or fields.Datetime.now()
            rec.exchange_rate = rec.currency_id.with_context(
                date=date)._get_conversion_rate(rec.company_currency_id,
                                                rec.currency_id
                                                )

    @api.depends('amount',
                 'currency_id',
                 'company_currency_id',
                 'invoice_id.date')
    def _compute_amount_currency(self):
        for rec in self:
            date = rec.invoice_id.date or fields.Datetime.now()
            rec.amount_currency = rec.currency_id.with_context(
                date=date).compute(rec.amount, rec.company_currency_id)
