# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    duration = fields.Integer(default=12)

    @api.onchange('duration')
    def duration_change(self):
        if self.order_line:
            self.order_line.update({'duration': self.duration})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    duration = fields.Integer()
