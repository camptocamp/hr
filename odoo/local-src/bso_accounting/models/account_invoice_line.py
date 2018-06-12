# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def _get_invoice_line_group_fields(self):
        res = super(AccountInvoiceLine, self)._get_invoice_line_group_fields()
        res.extend([
            'start_date',
            'end_date',
        ])
        return res
