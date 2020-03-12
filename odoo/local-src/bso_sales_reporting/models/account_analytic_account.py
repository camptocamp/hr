# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    invoice_line_ids = fields.One2many(
        string='Invoice Lines',
        comodel_name='account.invoice.line',
        inverse_name='account_analytic_id',
        readonly=True,
    )

    invoice_ids = fields.Many2many(
        string='Invoices',
        comodel_name='account.invoice',
        compute='_compute_invoice_ids',
    )

    @api.multi
    def _compute_invoice_ids(self):
        for rec in self:
            rec.invoice_ids = rec.invoice_line_ids.mapped('invoice_id.id')
