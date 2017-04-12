# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleRefusal(models.TransientModel):
    _name = 'sale.refusal'

    reason = fields.Text(
        required=True,
    )
    order_id = fields.Many2one(
        'sale.order'
    )

    @api.multi
    def refuse(self):
        res = False
        for wizard in self:
            wizard.order_id.refusal_reason = wizard.reason
            res = wizard.order_id.action_refuse()
        return res
