# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_disputed = fields.Boolean(
        string='Disputed',
        compute='_compute_disputed',
        store=True
    )

    @api.multi
    @api.depends('dispute_line_ids.state')
    def _compute_disputed(self):
        for rec in self:
            rec.is_disputed = any(line.state == 'dispute'
                                  for line in rec.dispute_line_ids)
