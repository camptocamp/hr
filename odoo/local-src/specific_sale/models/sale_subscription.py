# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    recurring_total = fields.Monetary(string='Monthly Total')
    period_total = fields.Monetary(
        string='Period Total',
        compute='_compute_period_total',
        readonly=True,
    )

    @api.depends('recurring_total', 'recurring_interval')
    def _compute_period_total(self):
        for sub in self:
            sub.period_total = sub.recurring_total * sub.recurring_interval

    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(SaleSubscription, self)._prepare_invoice_line(
            line=line, fiscal_position=fiscal_position)
        if self.recurring_interval:
            res['quantity'] = self.recurring_interval * res['quantity']
        return res
