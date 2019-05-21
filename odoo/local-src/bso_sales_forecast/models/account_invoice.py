# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, values):
        if 'state' not in values:
            return super(AccountInvoice, self).write(values)
        diff = self.env['forecast.line.diff']
        for rec in self:
            action = rec.get_action(values)
            if not action:
                continue
            if not rec.to_log():
                continue
            for line in rec.invoice_line_ids:
                fields_to_log = self.get_fields_to_log(line,
                                                       state=values['state'])
                diff.log(line._name, line.id, action, fields_to_log)
        return super(AccountInvoice, self).write(values)

    def get_action(self, values):
        if self.state != 'open' and values.get('state') == 'open':
            return 'create'
        if self.state == 'open' and 'state' in values \
                and values['state'] == 'cancel':
            return 'delete'
        if self.state in ('open', 'paid'):
            return 'update'
        return False

    def to_log(self):
        # check if updated sub company is related to a generated forecast
        # report
        generated_reports_companies = self._get_generated_reports_companies()
        if self.company_id not in generated_reports_companies:
            return False
        if not self.is_futur_invoice():
            return False
        return True

    def _get_generated_reports_companies(self):
        return self.env['forecast.report'].search([]).mapped('company_id')

    def is_futur_invoice(self):
        if not self.date_invoice:
            return False
        if self.date_invoice >= fields.Date.today():
            return True

    def get_fields_to_log(self, line, **kwargs):
        invoice = line.invoice_id
        state = kwargs.get('state', invoice.state)
        return {
            'amount': kwargs.get('price_subtotal', line.price_subtotal),
            'end_date': kwargs.get('date_invoice', invoice.date_invoice),
            'state': self._get_corresponding_state(state),
            'is_refund': 'refund' in invoice.type,
        }

    @staticmethod
    def _get_corresponding_state(state):
        if state in ('open', 'paid'):
            return 'open'
        return 'close'
