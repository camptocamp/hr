from odoo import models, fields, api


class BundleDetailsEPLLink(models.Model):
    _name = 'bundle.details.epl.link'
    _order = 'bundle_details_id_epl_route ASC,' \
             'bundle_details_id_epl_backup ASC,' \
             'sequence ASC,' \
             'id ASC'

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
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        compute='compute_currency_id'
    )
    sequence = fields.Integer(
        default=0
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
    link_id = fields.Many2one(
        string='Link',
        comodel_name='epl.link',
        required=True
    )
    latency = fields.Float(
        related='link_id.latency',
        readonly=True
    )
    bandwidth = fields.Integer(
        related='link_id.bandwidth',
        readonly=True
    )
    cable_id = fields.Many2one(
        string='Cable',
        related='link_id.cable_id',
        readonly=True
    )
    is_protected = fields.Boolean(
        related='link_id.is_protected',
        readonly=True
    )
    cost_upfront = fields.Float(
        string='Non Recurring Cost',
        compute='compute_cost_upfront'
    )
    cost = fields.Float(
        string='Recurring Cost',
        compute='compute_cost'
    )
    cost_per_mb = fields.Float(
        string='Recurring Cost / Mbps',
        compute='compute_cost_per_mb'
    )
    price_upfront = fields.Float(
        string='Non Recurring Price',
        compute='compute_price_upfront'
    )
    price = fields.Float(
        string='Recurring Price',
        compute='compute_price'
    )
    price_per_mb = fields.Float(
        string='Recurring Price / Mbps',
        compute='compute_price_per_mb'
    )

    # COMPUTES

    @api.depends('bundle_details_id_epl_route.currency_id',
                 'bundle_details_id_epl_backup.currency_id')
    def compute_currency_id(self):
        for rec in self:
            currency_id = rec.bundle_details_id_epl_route.currency_id \
                          or rec.bundle_details_id_epl_backup.currency_id
            rec.update({
                'currency_id': currency_id
            })

    @api.depends('link_id.currency_id', 'link_id.cost_upfront', 'currency_id')
    def compute_cost_upfront(self):
        for rec in self:
            cost_upfront = rec.link_id.currency_id.sudo().compute(
                from_amount=rec.link_id.cost_upfront,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'cost_upfront': cost_upfront
            })

    @api.depends('link_id.currency_id', 'link_id.cost', 'currency_id')
    def compute_cost(self):
        for rec in self:
            cost = rec.link_id.currency_id.sudo().compute(
                from_amount=rec.link_id.cost,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'cost': cost
            })

    @api.depends('cost', 'bandwidth')
    def compute_cost_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'cost_per_mb': rec.cost / rec.bandwidth
                })

    @api.depends('link_id.currency_id', 'link_id.price_upfront', 'currency_id')
    def compute_price_upfront(self):
        for rec in self:
            price_upfront = rec.link_id.currency_id.sudo().compute(
                from_amount=rec.link_id.price_upfront,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'price_upfront': price_upfront
            })

    @api.depends('link_id.currency_id', 'link_id.price', 'currency_id')
    def compute_price(self):
        for rec in self:
            price = rec.link_id.currency_id.sudo().compute(
                from_amount=rec.link_id.price,
                to_currency=rec.currency_id,
                round=False
            )
            rec.update({
                'price': price
            })

    @api.depends('price', 'bandwidth')
    def compute_price_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'price_per_mb': rec.price / rec.bandwidth
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
        domain = ['|',
                  ('a_device_id', '=', a_device_id),
                  ('z_device_id', '=', a_device_id)]
        if z_device_id:
            domain += ['|',
                       ('a_device_id', '=', z_device_id),
                       ('z_device_id', '=', z_device_id)]
        return self.env['epl.link'].sudo().search(domain)
