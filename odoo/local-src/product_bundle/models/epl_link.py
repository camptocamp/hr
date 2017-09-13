from odoo import models, fields, api, exceptions, _


class EplLink(models.Model):
    _name = 'epl.link'

    name = fields.Char(
        string='Name',
        compute='compute_name',
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='epl.device',
        index=True,
        required=True
    )
    a_pop_id = fields.Many2one(
        string='POP A',
        related='a_device_id.pop_id',
        required=True
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='epl.device',
        index=True,
        required=True
    )
    z_pop_id = fields.Many2one(
        string='POP Z',
        related='z_device_id.pop_id',
        required=True
    )
    bandwidth = fields.Float(
        string='Bandwidth',
        required=True
    )
    latency = fields.Float(
        string='Latency',
        required=True
    )
    latency_str = fields.Char(
        string='Latency',
        compute='compute_latency_str',
    )
    mrc = fields.Float(
        string='MRC',
        required=True
    )
    mrc_mb = fields.Float(
        string='MRC / Mb',
        compute='compute_mrc_mb',
        store=True
    )
    nrc = fields.Float(
        string='NRC'
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
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
    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('a_device_id', 'z_device_id', 'latency_str')
    def compute_name(self):
        for rec in self:
            rec.name = "%s <-> %s @ %s" % (rec.a_device_id.name,
                                           rec.z_device_id.name,
                                           rec.latency_str)

    @api.depends('latency')
    def compute_latency_str(self):
        for rec in self:
            rec.latency_str = "%.2fms" % rec.latency

    @api.depends('bandwidth', 'mrc')
    def compute_mrc_mb(self):
        for rec in self:
            rec.mrc_mb = (rec.mrc / rec.bandwidth) if rec.bandwidth else 0
