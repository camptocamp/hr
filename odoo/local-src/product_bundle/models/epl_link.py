from odoo import models, fields, api


class EplLink(models.Model):
    _name = 'epl.link'

    name = fields.Char(
        string='Name',
        compute='compute_name'
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='epl.device',
        index=True,
        required=True
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='epl.device',
        index=True,
        required=True
    )
    latency = fields.Float(
        string='Latency (ms)',
        required=True
    )
    bandwidth = fields.Integer(
        string='Bandwidth (Mbps)',
        required=True
    )
    partner_id = fields.Many2one(
        string='Provider',
        comodel_name='res.partner'
    )
    cable_id = fields.Many2one(
        string='Cable',
        comodel_name='epl.cable'
    )
    is_protected = fields.Boolean(
        string='Is Protected',
        default=False
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    cost_upfront = fields.Float(
        string='Non Recurring Cost',
    )
    cost = fields.Float(
        string='Recurring Cost',
        required=True
    )
    cost_per_mb = fields.Float(
        string='Recurring Cost / Mbps',
        compute='compute_cost_per_mb'
    )
    price_upfront = fields.Float(
        string='Non Recurring Price'
    )
    price = fields.Float(
        string='Recurring Price',
        required=True
    )
    price_per_mb = fields.Float(
        string='Recurring Price / Mbps',
        compute='compute_price_per_mb'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('a_device_id.name', 'z_device_id.name', 'latency',
                 'is_protected')
    def compute_name(self):
        for rec in self:
            link_name = "%s <-> %s @ %.2fms" % (rec.a_device_id.name,
                                                rec.z_device_id.name,
                                                rec.latency)
            if rec.is_protected:
                link_name += " (Protected)"
            rec.update({
                'name': link_name
            })

    @api.depends('cost', 'bandwidth')
    def compute_cost_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'cost_per_mb': rec.cost / rec.bandwidth
                })

    @api.depends('price', 'bandwidth')
    def compute_price_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'price_per_mb': rec.price / rec.bandwidth
                })
