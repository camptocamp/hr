# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class NetworkLink(models.Model):
    _name = 'bso.network.link'

    def _default_get_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(required=True)
    pop1_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP A',
                              required=True)
    pop1_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP A device',
                                     required=True)
    pop2_id = fields.Many2one(comodel_name='bso.network.pop',
                              string='POP B',
                              required=True)
    pop2_device_id = fields.Many2one(comodel_name='bso.network.device',
                                     string='POP B device',
                                     required=True)
    bandwith = fields.Float()
    latency = fields.Float()
    mrc = fields.Float()
    nrc = fields.Float()
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self._default_get_currency()
    )
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Partner")
    cablesystem_id = fields.Many2one(comodel_name='bso.network.cablesystem',
                                     string="Cable system")
    active = fields.Boolean('Active', default=True)
    is_protected = fields.Boolean('Is protected', default=False)
    bso_id = fields.Integer(required=True)


class NetworkDevice(models.Model):
    _name = 'bso.network.device'

    name = fields.Char(required=True)
    pop_id = fields.Many2one(comodel_name='bso.network.pop',
                             string='POP',
                             required=True)
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Partner")
    active = fields.Boolean('Active', default=True)
    bso_id = fields.Integer(required=True)


class NetworkPop(models.Model):
    _name = 'bso.network.pop'

    name = fields.Char(required=True)
    link_ids = fields.Many2many('bso.network.link')
    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Partner")
    geo_area = fields.Char(string='Geographical area')
    longitude = fields.Float()
    latitude = fields.Float()
    active = fields.Boolean('Active', default=True)
    bso_id = fields.Integer(required=True)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        res = super(NetworkPop, self).create(values)
        vals = {'name': res.name,
                'code': '%s' % res.name.replace('-', ''),
                }
        xml_id = 'wh_pop_%s' % res.id
        warehouse = self.env['stock.warehouse'].create(vals)
        vls = {
            'name': xml_id,
            'module': '__setup__',
            'model': 'stock.warehouse',
            'res_id': warehouse.id
        }
        self.env['ir.model.data'].create(vls)

        return res


class NetworkCableSystem(models.Model):
    _name = 'bso.network.cablesystem'

    name = fields.Char(required=True)
    active = fields.Boolean('Active', default=True)
    bso_id = fields.Integer(required=True)
