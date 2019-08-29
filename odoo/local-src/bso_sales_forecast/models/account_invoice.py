# -*- coding: utf-8 -*-

from odoo import models, api


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
            for line in rec.invoice_line_ids:
                fields_to_log = rec.get_fields_to_log(line, values['state'])
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

    # def is_futur_invoice(self):
    #     if not self.date_invoice:
    #         return False
    #     if self.date_invoice >= fields.Date.today():
    #         return True

    def get_fields_to_log(self, line, state):
        invoice = line.invoice_id
        return {
            'company_id': invoice.company_id.id,
            'amount': line.price_subtotal,
            'end_date': invoice.date_invoice,
            'state': self._get_corresponding_state(state),
            'is_refund': 'refund' in invoice.type,
        }

    @staticmethod
    def _get_corresponding_state(state):
        if state in ('open', 'paid'):
            return 'open'
        return 'close'
