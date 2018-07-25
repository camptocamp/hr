from odoo import models, fields, api


class BundleDetailsEPLLink(models.Model):
    _name = 'bundle.details.epl.link'
    _order = 'bundle_details_id ASC,' \
             'sequence ASC,' \
             'id ASC'

    bundle_details_id = fields.Many2one(
        string='Bundle Details',
        comodel_name='bundle.details',
        ondelete='cascade',
        readonly=True
    )
    currency_id = fields.Many2one(
        related='bundle_details_id.currency_id',
        readonly=True,
        store=True
    )
    is_epl_backup = fields.Boolean(
        string='Is EPL Backup'
    )
    is_epl_route = fields.Boolean(  # Used for a_device_id domain condition
        string='Is EPL Route',
        compute='compute_is_epl_route',
        store=True
    )
    sequence = fields.Integer(
        default=0
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='backbone.device',
        required=True
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='backbone.device',
        required=True
    )
    link_id = fields.Many2one(
        string='Link',
        comodel_name='backbone.link',
        required=True
    )
    is_wireless = fields.Boolean(
        related='link_id.is_wireless',
        readonly=True,
        store=True
    )
    latency = fields.Float(
        related='link_id.latency',
        readonly=True,
        store=True
    )
    bandwidth = fields.Integer(
        related='link_id.bandwidth',
        readonly=True,
        store=True
    )
    cable_system = fields.Char(
        related='link_id.cable_system',
        readonly=True,
        store=True
    )
    is_protected = fields.Boolean(
        related='link_id.is_protected',
        readonly=True,
        store=True
    )
    mrc = fields.Monetary(
        string='MRC',
        compute='compute_mrc',
        store=True
    )
    mrc_mb = fields.Monetary(
        string='MRC / Mb',
        compute='compute_mrc_mb',
        store=True
    )
    mrr = fields.Monetary(
        string='MRR',
        compute='compute_mrr',
        store=True
    )
    mrr_mb = fields.Monetary(
        string='MRR / Mb',
        compute='compute_mrr_mb',
        store=True
    )

    # COMPUTES

    @api.depends('is_epl_backup')
    def compute_is_epl_route(self):
        for rec in self:
            rec.update({
                'is_epl_route': not rec.is_epl_backup
            })

    @api.depends('link_id.currency_id', 'link_id.mrc', 'currency_id')
    def compute_mrc(self):
        for rec in self:
            mrc = rec.link_id.currency_id.compute(
                from_amount=rec.link_id.mrc,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'mrc': mrc
            })

    @api.depends('mrc', 'bandwidth')
    def compute_mrc_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'mrc_mb': rec.mrc / rec.bandwidth
                })

    @api.depends('link_id.currency_id', 'link_id.mrr', 'currency_id')
    def compute_mrr(self):
        for rec in self:
            mrr = rec.link_id.currency_id.compute(
                from_amount=rec.link_id.mrr,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'mrr': mrr
            })

    @api.depends('mrr', 'bandwidth')
    def compute_mrr_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'mrr_mb': rec.mrr / rec.bandwidth
                })

    # DOMAINS

    @api.onchange('a_device_id')
    def domain_z_device_id(self):
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
    def domain_link_id(self):
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
        domain = [('bandwidth', '>=', self.bundle_details_id.epl_bandwidth),
                  '|',
                  ('a_device_id', '=', a_device_id),
                  ('z_device_id', '=', a_device_id)]
        if z_device_id:
            domain += ['|',
                       ('a_device_id', '=', z_device_id),
                       ('z_device_id', '=', z_device_id)]
        return self.env['backbone.link'].search(domain)
