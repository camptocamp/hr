# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductUom(models.Model):
    _inherit = 'product.uom'

    recurring = fields.Boolean(
        string='Recurring',
        compute='_compute_recurring',
        store=True
    )

    @api.depends('category_id.recurring')
    def _compute_recurring(self):
        for record in self:
            record.recurring = record.category_id.recurring
