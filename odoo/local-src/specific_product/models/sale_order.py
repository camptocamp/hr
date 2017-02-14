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
                 'network_backup_link_ids',
                 'network_backup_link_ids.mrc',
                 'network_backup_link_ids.mrc_bd',
                 'asked_bandwidth')
    def get_amounts_backup(self):
        """ compute nrc and mrc from link lines """
        for rec in self:
            if rec.product_id.is_epl:
                rec.mrc_backup = (
                    rec.asked_bandwidth *
                    sum(rec.mapped('network_backup_link_ids.mrc_bd'))
                )

    @api.depends('product_id',
                 'network_link_ids',
                 'network_link_ids.mrc',
                 'network_link_ids.mrc_bd',
                 'asked_bandwidth')
    def get_amounts(self):
        """ compute mrc from link lines """
        for rec in self:
            if rec.product_id.is_epl:
                rec.mrc = (
                    rec.asked_bandwidth *
                    sum(rec.mapped('network_link_ids.mrc_bd'))
                )
                if rec.mapped('network_link_ids.bandwith'):
                    rec.bandwith = min(rec.mapped('network_link_ids.bandwith'))
                else:
                    rec.bandwith = 0
                rec.latency = sum(rec.mapped('network_link_ids.latency'))

    @api.depends('product_id', 'mrc', 'duration', 'asked_bandwidth',
                 'mrc_backup', 'find_backup',
                 'backup_discount_percent')
    def get_computed_route_amounts(self):
        for rec in self:
            if rec.product_id.is_epl:
                rec.price_main_route = rec.mrc  # * rec.duration
                rec.backup_discount_amount = rec.price_main_route * .5  # 50%
                rec.price_backup_route = rec.mrc_backup  # * rec.duration
                rec.price_backup_route_discounted = (
                    rec.price_main_route *
                    (100 - rec.backup_discount_percent) / 100
                )
                if rec.find_backup and rec.backup_discount_percent == 100:
                    rec.backup_discount_percent = 50
                if not rec.find_backup:
                    rec.backup_discount_percent = 100

    latency = fields.Float(compute='get_amounts', store=True)
    bandwith = fields.Float(string='Bandwidth', compute='get_amounts',
                            store=True)
    geo_area = fields.Char()
    mrc = fields.Float(compute='get_amounts', store=True)
    mrc_backup = fields.Float(compute='get_amounts_backup', store=True)
    duration = fields.Integer()
    price_main_route = fields.Float(compute='get_computed_route_amounts',
                                    store=True)
    price_backup_route = fields.Float(compute='get_computed_route_amounts',
                                      store=True)
    price_backup_route_discounted = fields.Float(
        compute='get_computed_route_amounts', store=True)
    pop1_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP A')
    pop2_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP B')
    find_backup = fields.Boolean(default=True)
    network_link_ids = fields.One2many('sale.order.line.network.link',
                                       'sale_line_id',
                                       domain=[('is_backup', '=', False)],
                                       copy=True)
    network_backup_link_ids = fields.One2many(
        'sale.order.line.network.link',
        'sale_line_id',
        domain=[('is_backup', '=', True)],
        copy=True)
    backup_discount_amount = fields.Float(compute='get_computed_route_amounts',
                                          store=True)
    backup_discount_percent = fields.Float(default=50.)
    is_epl = fields.Boolean(related='product_id.is_epl', readonly=True)
    epl_warnings = fields.Text()
    asked_bandwidth = fields.Float(default=1.0)
    route_sort = fields.Selection(selection=[('1', 'Latency'),
                                             ('2', 'MRC'),
                                             ('3', 'Latency/MRC')],
                                  default='1',
                                  copy=True,
                                  )

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.is_epl:
            self.mrc = self.product_id.mrc
        return res

    @api.onchange('product_id', 'mrc', 'duration')
    def onchange_nrc_mrc(self):
        if self.product_id.is_epl:
            self.price_main_route = self.mrc  # * self.duration
            self.backup_discount_amount = self.price_main_route * .5  # 50%

    @api.onchange('product_id', 'mrc_backup', 'duration',
                  'price_backup_route', 'backup_discount_amount',
                  'find_backup')
    def onchange_mrc_backup(self):
        if self.product_id.is_epl:
            if self.find_backup:
                self.price_backup_route = self.mrc_backup  # * self.duration

    @api.onchange('backup_discount_percent', 'price_backup_route')
    def onchange_backup_discount_percent(self):
        self.price_backup_route_discounted = (
            self.price_main_route *
            (100 - self.backup_discount_percent) / 100
        )

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update(duration=self.duration,
                   mrc=self.mrc,
                   price_unit=self.price_unit)
        return res

    @api.onchange('price_backup_route_discounted', 'price_main_route')
    def onchange_prices(self):
        if self.is_epl:
            self.price_unit = (
                self.price_backup_route_discounted + self.price_main_route
            )

    def get_link(self, e_start, e_end):
        """ take equipment start en equipement end
            returns ID of the link if found, otherwise False
        """
        link = self.env['bso.network.link'].search(
            [('pop1_device_id.name', '=', e_start),
             ('pop2_device_id.name', '=', e_end)], limit=1)
        if not link:
            link = self.env['bso.network.link'].search(
                [('pop1_device_id.name', '=', e_end),
                 ('pop2_device_id.name', '=', e_start)], limit=1)
        return link

    def fill_main_route(self, route_dict):
        link_vals = []
        incr = 0
        for detail in route_dict['details']:
            incr += 10
            vals = {'sequence': incr}
            link = self.get_link(detail['equip_start'],
                                 detail['equip_end'])
            if link:
                vals['link_id'] = link.id
                vals['mrc'] = link.mrc
                vals['name'] = link.name
                vals['pop1_id'] = link.pop1_id.id
                vals['pop1_device_id'] = link.pop1_device_id.id
                vals['pop2_id'] = link.pop2_id.id
                vals['pop2_device_id'] = link.pop2_device_id.id
                vals['bandwith'] = link.bandwith
                vals['latency'] = link.latency
                vals['cablesystem_id'] = link.cablesystem_id.id

                link_vals.append((0, 0, vals))
        return self.update({'network_link_ids': link_vals})

    def fill_backup_route(self, route_dict):
        link_vals = []
        incr = 0
        for detail in route_dict['details']:
            incr += 10
            vals = {'sequence': incr, 'is_backup': True}
            link = self.get_link(detail['equip_start'],
                                 detail['equip_end'])
            if link:
                vals['link_id'] = link.id
                vals['mrc'] = link.mrc
                vals['name'] = link.name
                vals['pop1_id'] = link.pop1_id.id
                vals['pop1_device_id'] = link.pop1_device_id.id
                vals['pop2_id'] = link.pop2_id.id
                vals['pop2_device_id'] = link.pop2_device_id.id
                vals['bandwith'] = link.bandwith
                vals['latency'] = link.latency
                vals['cablesystem_id'] = link.cablesystem_id.id

                link_vals.append((0, 0, vals))
        return self.update({'network_backup_link_ids': link_vals})

    def empty_routes(self):
        return self.update({'network_backup_link_ids': [(5, 0)],
                           'network_link_ids': [(5, 0)]
                            })

    @api.onchange('pop1_id', 'pop2_id', 'find_backup', 'route_sort')
    def get_route(self):
        """ call(self, start, end, user, sort=1, backup=1, details=1): """
        res = {'warning': ''}
        self.empty_routes()
        if self.pop1_id and self.pop2_id:
            backup = self.find_backup and 1 or 0
            result = self.order_id.company_id.network_api_id.call(
                self.pop1_id.name,
                self.pop2_id.name,
                self.env.user,
                backup=backup,
                sort=int(self.route_sort)
            )
            self.epl_warnings = '\n'.join(result['warnings'])
            self.fill_main_route(result['route'])
            if result['backup']:
                self.fill_backup_route(result['backup'])
            if result['warnings']:
                res['warning'] = {'message': self.epl_warnings}
                return res


class SaleOrderLineNetworkLink(models.Model):
    _name = 'sale.order.line.network.link'

    sequence = fields.Integer(default=10)
    sale_line_id = fields.Many2one(comodel_name='sale.order.line')
    is_backup = fields.Boolean(default=False)
    link_id = fields.Many2one(comodel_name='bso.network.link')
    name = fields.Char()
    pop1_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP A')
    pop1_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP A device')
    pop2_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP B')
    pop2_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP B device')
    bandwith = fields.Float(string='Bandwidth')
    latency = fields.Float()
    mrc = fields.Float()
    mrc_bd = fields.Float(compute='_get_mrc_bandwith', digits=(16, 3),
                          store=True)
    cablesystem_id = fields.Many2one(comodel_name='bso.network.cablesystem',
                                     string='Cable system')

    @api.depends('mrc', 'bandwith')
    def _get_mrc_bandwith(self):
        for rec in self:
            if rec.bandwith:
                rec.mrc_bd = rec.mrc / rec.bandwith

    @api.onchange('link_id')
    def onchange_link_id(self):
        if self.link_id:
            self.update(
                {'pop1_id': self.link_id.pop1_id,
                 'pop1_device_id': self.link_id.pop1_device_id,
                 'pop2_id': self.link_id.pop2_id,
                 'pop2_device_id': self.link_id.pop2_device_id,
                 'bandwith': self.link_id.bandwith,
                 'latency': self.link_id.latency,
                 'mrc': self.link_id.mrc,
                 'cablesystem_id': self.link_id.cablesystem_id,
                 }
            )
