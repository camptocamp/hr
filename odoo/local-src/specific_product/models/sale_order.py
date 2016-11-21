# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

import random


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    duration = fields.Integer(default=12)

    @api.onchange('duration')
    def duration_change(self):
        if self.order_line:
            self.order_line.update({'duration': self.duration})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    latency = fields.Float()
    bandwith = fields.Float()
    geo_area = fields.Char()

    mrc = fields.Float()
    nrc = fields.Float()
    duration = fields.Integer(readonly=True)

    @api.multi
    def estimate_price(self):
        self.ensure_one()
        self.price_unit = random.randint(0, 1500)*random.random()

    @api.onchange('product_id', 'duration')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.nrc = self.product_id.nrc
            self.mrc = self.product_id.mrc
        return res
