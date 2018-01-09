# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    payment_mode_id = fields.Many2one(comodel_name='account.payment.mode',
                                      string='Payment mode'
                                      )

    @api.multi
    def _prepare_invoice_data(self):
        self.ensure_one()
        res = super(SaleSubscription, self)._prepare_invoice_data()

        # propagate payment_mode from subscription to invoice
        res['payment_mode_id'] = self.payment_mode_id.id

        return res
