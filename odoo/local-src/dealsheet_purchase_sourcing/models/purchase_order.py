# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sourced_dealsheet_line_id = fields.Many2one(
        string='Sourced dealsheet line',
        comodel_name='sale.dealsheet.line',
        readonly=True,
        ondelete='set null',
    )
