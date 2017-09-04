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
            sale_orders = (invoice.invoice_line_ids.mapped('sale_line_ids')
                                                   .mapped('order_id'))
            for so in sale_orders:
                if so.all_mrc_delivered():
                    so.subscription_id = so.create_contract()
        return res
