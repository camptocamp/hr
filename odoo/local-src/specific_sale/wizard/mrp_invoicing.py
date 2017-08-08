# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class MrpInvoicing(models.TransientModel):
    _name = 'mrp.invoicing'

    ref_date = fields.Datetime(
        required=True,
    )
    # order_id = fields.Many2one(
    #     'sale.order'
    # )

    @api.multi
    def ok(self):
        res = False
        for wizard in self:
            wizard.ref_date = wizard.ref_date
            # res = wizard.order_id.action_refuse()
        return res
