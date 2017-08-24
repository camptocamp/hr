# -*- coding: utf-8 -*-
# Author: Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sourced_sale_line_id = fields.Many2one(
        string='Sourced sale order line',
        comodel_name='sale.order.line',
        readonly=True,
        ondelete='set null',
    )
