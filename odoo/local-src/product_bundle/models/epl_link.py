from odoo import models, fields, api


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
    mrc = fields.Monetary(
        string='MRC',
        currency_field='currency_id',
        required=True
    )
    mrc_per_mb = fields.Monetary(
        string='MRC/Mbps',
        currency_field='currency_id',
        compute='compute_mrc_per_mb'
    )
    nrc = fields.Monetary(
        string='NRC',
        currency_field='currency_id'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('a_device_id', 'z_device_id', 'latency')
    def compute_name(self):
        for rec in self:
            link_name = "%s <-> %s @ %.2fms" % (rec.a_device_id.name,
                                                rec.z_device_id.name,
                                                rec.latency)
            if rec.is_protected:
                link_name += " (Protected)"
            rec.name = link_name

    @api.depends('mrc', 'bandwidth')
    def compute_mrc_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.mrc_per_mb = rec.mrc / rec.bandwidth
