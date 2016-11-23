# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    duration = fields.Integer(default=12)

    @api.onchange('duration')
    def duration_change(self):
        if self.invoice_line_ids:
            self.invoice_line_ids.update({'duration': self.duration})


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    latency = fields.Float()
    bandwith = fields.Float()
    geo_area = fields.Char()

    mrc = fields.Float()
    nrc = fields.Float()
    duration = fields.Integer()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            self.nrc = self.product_id.nrc
            self.mrc = self.product_id.mrc
        return res

    @api.onchange('product_id', 'mrc', 'nrc', 'duration')
    def onchange_nrc_mrc(self):
        if self.product_id.is_epl:
            self.price_unit = self.nrc + (self.mrc * self.duration)
