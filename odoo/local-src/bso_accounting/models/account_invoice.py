# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_invoice_group_fields(self):
        res = super(AccountInvoice, self)._get_invoice_group_fields()
        res.extend([
            'fiscal_position_id',
            'payment_mode_id',
        ])
        return res
