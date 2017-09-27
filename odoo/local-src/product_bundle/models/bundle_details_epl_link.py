from odoo import models, fields, api


class BundleDetailsEPLLink(models.Model):
    _name = 'bundle.details.epl.link'
    _order = 'bundle_details_id_epl_route ASC,' \
             'bundle_details_id_epl_backup ASC,' \
             'sequence ASC,' \
             'id ASC'

    sequence = fields.Integer(
        default=0
    )
    bundle_details_id_epl_route = fields.Many2one(
        string='Bundle Details EPL Route',
        comodel_name='bundle.details',
        ondelete='cascade'
    )
    bundle_details_id_epl_backup = fields.Many2one(
        string='Bundle Details EPL Backup',
        comodel_name='bundle.details',
        ondelete='cascade'
    )
    link_id = fields.Many2one(
        string='Link',
        comodel_name='epl.link',
        required=True
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='epl.device',
        required=True
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='epl.device',
        required=True
    )
    latency = fields.Float(
        string='Latency (ms)',
        related='link_id.latency',
        readonly=True
    )
    bandwidth = fields.Integer(
        string='Bandwidth (Mbps)',
        related='link_id.bandwidth',
        readonly=True
    )
    cable_id = fields.Many2one(
        string='Cable',
        related='link_id.cable_id',
        readonly=True
    )
    is_protected = fields.Boolean(
        string='Is Protected',
        related='link_id.is_protected',
        readonly=True
    )
    local_currency_id = fields.Many2one(
        string='Local Currency',
        related='link_id.currency_id',
        readonly=True
    )
    local_price = fields.Monetary(
        string='Local Price',
        related='link_id.mrc',
        currency_field='local_currency_id',
        readonly=True
    )
    local_price_per_mb = fields.Monetary(
        string='Local Price/Mbps',
        related='link_id.mrc_per_mb',
        currency_field='local_currency_id',
        readonly=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        compute='compute_price'
    )
    price_per_mb = fields.Monetary(
        string='Price/Mbps',
        currency_field='currency_id',
        compute='compute_price_per_mb'
    )

    # COMPUTES

    @api.depends('link_id', 'currency_id')
    def compute_price(self):
        for rec in self:
            rec.price = rec.local_currency_id.sudo().compute(
                from_amount=rec.local_price,
                to_currency=rec.currency_id
            )

    @api.depends('link_id', 'price')
    def compute_price_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.price_per_mb = rec.price / rec.bandwidth

    # ONCHANGES

    @api.onchange('a_device_id')
    def set_domain_z_device_id(self):
        for rec in self:
            rec.z_device_id = False
            if not rec.a_device_id:
                continue
            links = self.get_link_ids(rec.a_device_id.id)
            device_keys = ('a_device_id', 'z_device_id')
            device_all_ids = [l[d].id for l in links for d in device_keys]
            device_ids = list(set(device_all_ids) - {rec.a_device_id.id})
            if len(device_ids) == 1:
                rec.z_device_id = device_ids[0]
            return {'domain': {'z_device_id': [('id', 'in', device_ids)]}}

    @api.onchange('a_device_id', 'z_device_id')
    def set_domain_link_id(self):
        for rec in self:
            rec.link_id = False
            if not rec.a_device_id or not rec.z_device_id:
                continue
            links = self.get_link_ids(rec.a_device_id.id,
                                      rec.z_device_id.id)
            link_ids = [link.id for link in links]
            if len(link_ids) == 1:
                rec.link_id = link_ids[0]
            return {'domain': {'link_id': [('id', 'in', link_ids)]}}

    # TOOLS

    @api.model
    def get_link_ids(self, a_device_id, z_device_id=0):
        domain = ['|',
                  ('a_device_id', '=', a_device_id),
                  ('z_device_id', '=', a_device_id)]
        if z_device_id:
            domain += ['|',
                       ('a_device_id', '=', z_device_id),
                       ('z_device_id', '=', z_device_id)]
        return self.env['epl.link'].sudo().search(domain)
