# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def get_suitable_payment_mode(self):
        s_args = [
            ('company_id', '=', self.company_id.id),
            ('payment_type', '=', 'inbound'),
            ]

        if self.currency_id != self.company_id.currency_id:
            s_args.append(
                ('fixed_journal_id.currency_id', '=', self.currency_id.id)
            )
        else:
            s_args.append(
                ('fixed_journal_id.currency_id', '=', False)
            )

        payment = self.env['account.payment.mode'].search(s_args, limit=1)
        return payment

    @api.onchange('currency_id')
    def onchange_currency(self):
        payment_mode = self.get_suitable_payment_mode()
        if not payment_mode:
            # get the one defined on partner
            payment_mode = self.partner_id.customer_payment_mode_id
        self.payment_mode_id = payment_mode.id
