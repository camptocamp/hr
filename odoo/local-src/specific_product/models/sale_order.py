# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    duration = fields.Integer(default=12)

    @api.onchange('duration')
    def duration_change(self):
        if self.order_line:
            self.order_line.update({'duration': self.duration})

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        res = super(SaleOrder, self)._prepare_invoice()
        res.update(duration=self.duration)
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id',
                 'network_link_ids',
                 'network_link_ids.nrc',
                 'network_link_ids.mrc')
    def get_amounts(self):
        """ compute nrc and mrc from link lines """
        for rec in self:
            if rec.product_id.is_epl:
                rec.nrc = sum(rec.mapped('network_link_ids.nrc'))
                rec.mrc = sum(rec.mapped('network_link_ids.mrc'))
                rec.bandwith = min(rec.mapped('network_link_ids.bandwith'))
                rec.latency = sum(rec.mapped('network_link_ids.latency'))

    latency = fields.Float(compute='get_amounts', store=True)
    bandwith = fields.Float(compute='get_amounts', store=True)
    geo_area = fields.Char()
    mrc = fields.Float(compute='get_amounts', store=True)
    nrc = fields.Float(compute='get_amounts', store=True)
    duration = fields.Integer()
    pop1_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP A')
    pop2_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP B')
    network_link_ids = fields.One2many('sale.order.line.network.link',
                                       'sale_line_id')

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.nrc = self.product_id.nrc
            self.mrc = self.product_id.mrc
        return res

    @api.onchange('product_id', 'mrc', 'nrc', 'duration')
    def onchange_nrc_mrc(self):
        if self.product_id.is_epl:
            self.price_unit = self.nrc + (self.mrc * self.duration)

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update(duration=self.duration,
                   nrc=self.nrc,
                   mrc=self.mrc,
                   price_unit=self.price_unit)
        return res


class SaleOrderLineNetworkLink(models.Model):
    _name = 'sale.order.line.network.link'

    sequence = fields.Integer(default=10)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line')
    link_id = fields.Many2one(comodel_name='bso.network.link')
    name = fields.Char(related='link_id.name', store=True)
    pop1_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP A', related='link_id.pop1_id')
    pop1_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP A device',
                                     related='link_id.pop1_device_id')
    pop2_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP B', related='link_id.pop2_id')
    pop2_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP A device',
                                     related='link_id.pop2_device_id')
    bandwith = fields.Float(related='link_id.bandwith')
    latency = fields.Float(related='link_id.latency')
    mrc = fields.Float(related='link_id.mrc')
    nrc = fields.Float(related='link_id.nrc')
    cablesystem_id = fields.Many2one(comodel_name='bso.network.cablesystem',
                                     string='Cable system',
                                     related='link_id.cablesystem_id')
