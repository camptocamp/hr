from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BundleDetailsEPL(models.Model):
    _inherit = 'bundle.details'

    # EPL VARIABLES

    epl_name = fields.Char(
        string='Name',
        compute='compute_epl_name',
        store=True
    )
    epl_description = fields.Text(
        string='Description',
        compute='compute_epl_description',
        store=True
    )
    epl_bandwidth = fields.Integer(
        string="Bandwidth (Mbps)",
        default=100
    )

    # EPL ROUTE VARIABLES

    epl_route = fields.One2many(
        string='Route Path',
        comodel_name='bundle.details.epl.link',
        inverse_name='bundle_details_id',
        domain=[('is_epl_backup', '=', False)],
        context={'default_is_epl_backup': False}
    )
    epl_route_first_device_id = fields.Many2one(
        string='Route First Device',
        comodel_name='backbone.device',
        compute='compute_epl_route_first_device_id',
        store=True
    )
    epl_route_last_device_id = fields.Many2one(
        string='Route Last Device',
        comodel_name='backbone.device',
        compute='compute_epl_route_last_device_id',
        store=True
    )
    epl_route_latency = fields.Float(
        string='Route Latency (ms)',
        digits=(7, 3),
        compute='compute_epl_route_latency',
        store=True
    )
    epl_route_mrc_mb = fields.Float(
        string='Route MRC / Mb',
        compute='compute_epl_route_mrc_mb',
        store=True
    )
    epl_route_mrr_mb = fields.Float(
        string='Route MRR / Mb',
        compute='compute_epl_route_mrr_mb',
        store=True
    )
    epl_route_mrc = fields.Float(
        string='Route MRC',
        compute='compute_epl_route_mrc',
        store=True
    )
    epl_route_mrr = fields.Float(
        string='Route MRR',
        compute='compute_epl_route_mrr',
        store=True
    )

    # EPL BACKUP VARIABLES

    epl_backup = fields.One2many(
        string='Backup Path',
        comodel_name='bundle.details.epl.link',
        inverse_name='bundle_details_id',
        domain=[('is_epl_backup', '=', True)],
        context={'default_is_epl_backup': True}
    )
    epl_backup_first_device_id = fields.Many2one(
        string='Backup First Device',
        comodel_name='backbone.device',
        compute='compute_epl_backup_first_device_id',
        store=True
    )
    epl_backup_last_device_id = fields.Many2one(
        string='Backup Last Device',
        comodel_name='backbone.device',
        compute='compute_epl_backup_last_device_id',
        store=True
    )
    epl_backup_latency = fields.Float(
        string='Backup Latency (ms)',
        digits=(7, 3),
        compute='compute_epl_backup_latency',
        store=True
    )
    epl_backup_discount = fields.Integer(
        string='Backup Discount (%)',
        default=50
    )
    epl_backup_mrc_mb = fields.Float(
        string='Backup MRC / Mb',
        compute='compute_epl_backup_mrc_mb',
        store=True
    )
    epl_backup_mrr_mb = fields.Float(
        string='Backup MRR / Mb',
        compute='compute_epl_backup_mrr_mb',
        store=True
    )
    epl_backup_mrc = fields.Float(
        string='Backup MRC',
        compute='compute_epl_backup_mrc',
        store=True
    )
    epl_backup_mrr = fields.Float(
        string='Backup MRR',
        compute='compute_epl_backup_mrr',
        store=True
    )

    # EPL PRODUCTS VARIABLES

    epl_products = fields.One2many(
        string='Products',
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_id',
        domain=[('is_epl', '=', True)],
        context={'default_is_epl': True}
    )
    epl_products_mrc = fields.Float(
        string='Products MRC',
        compute='compute_epl_products_mrc',
        store=True
    )
    epl_products_mrr = fields.Float(
        string='Products MRR',
        compute='compute_epl_products_mrr',
        store=True
    )
    epl_products_mrc_mb = fields.Float(
        string='Products MRC / Mb',
        compute='compute_epl_products_mrc_mb',
        store=True
    )
    epl_products_mrr_mb = fields.Float(
        string='Products MRR / Mb',
        compute='compute_epl_products_mrr_mb',
        store=True
    )
    epl_products_nrr = fields.Float(
        string='Products NRR',
        compute='compute_epl_products_nrr',
        store=True
    )

    # EPL DETAILS

    epl_latency = fields.Float(
        string='Latency (ms)',
        related='epl_route_latency'
    )
    epl_side_a = fields.Char(
        string='Side A'
    )
    epl_side_z = fields.Char(
        string='Side Z'
    )

    # EPL PRICE & COST

    epl_mrc_mb = fields.Float(
        string='MRC / Mb',
        compute='compute_epl_mrc_mb',
        help=_('(Route MRC + Backup MRC + Products MRC) / Bandwidth'),
        store=True
    )
    epl_mrr_mb = fields.Float(
        string='MRR / Mb',
        compute='compute_epl_mrr_mb',
        help=_('(Route MRR + Backup MRR + Products MRR) / Bandwidth'),
        store=True
    )
    epl_mrc = fields.Float(
        string='MRC',
        compute='compute_epl_mrc',
        help=_('Route MRC + Backup MRC + Products MRC'),
        store=True
    )
    dflt_epl_mrr = fields.Float(
        string='Default MRR',
        compute='compute_dflt_epl_mrr',
        help=_('Route MRR + Backup MRR + Products MRR'),
        store=True
    )
    epl_mrr = fields.Float(
        string='MRR',
        help=_('Route MRR + Backup MRR + Products MRR')
    )
    epl_nrr = fields.Float(
        string='NRR'
    )

    # EPL ONCHANGES

    @api.onchange('epl_route_first_device_id')
    def onchange_epl_route_first_device_id(self):
        for rec in self:
            rec.update({
                'epl_side_a': rec.epl_route_first_device_id.pop_id.address
            })

    @api.onchange('epl_route_last_device_id')
    def onchange_epl_route_last_device_id(self):
        for rec in self:
            rec.update({
                'epl_side_z': rec.epl_route_last_device_id.pop_id.address
            })

    @api.onchange('dflt_epl_mrr')
    def onchange_dflt_epl_mrr(self):
        for rec in self:
            rec.update({
                'epl_mrr': rec.dflt_epl_mrr
            })

    @api.onchange('epl_products_nrr')
    def onchange_epl_products_nrr(self):
        for rec in self:
            rec.update({
                'epl_nrr': rec.epl_products_nrr
            })

    # EPL VARIABLES COMPUTES

    @api.depends('epl_bandwidth', 'epl_latency', 'epl_backup',
                 'epl_route_first_device_id.pop_id.name',
                 'epl_route_last_device_id.pop_id.name')
    def compute_epl_name(self):
        for rec in self:
            epl_name = "%s %sM [%s <-> %s] @ %s ms" \
                       % (rec.bundle_id.name,
                          rec.epl_bandwidth,
                          rec.epl_route_first_device_id.pop_id.name,
                          rec.epl_route_last_device_id.pop_id.name,
                          rec.epl_latency)
            if rec.epl_backup:
                epl_name += " (Protected)"
            rec.update({
                'epl_name': epl_name
            })

    @api.depends('epl_bandwidth', 'epl_latency', 'epl_backup',
                 'epl_side_a', 'epl_side_z')
    def compute_epl_description(self):
        for rec in self:
            epl_description = [
                "Bandwidth: %s Mbps" % rec.epl_bandwidth,
                "Latency (est.): %s ms" % rec.epl_latency,
                "Protection: %s" % "Yes" if rec.epl_backup else "No",
                "Side A: %s" % rec.epl_side_a,
                "Side Z: %s" % rec.epl_side_z
            ]
            rec.update({
                'epl_description': "\n".join(epl_description)
            })

    # EPL ROUTE COMPUTES

    @api.depends('epl_route.a_device_id')
    def compute_epl_route_first_device_id(self):
        for rec in self:
            if not rec.epl_route:
                continue
            rec.update({
                'epl_route_first_device_id': rec.epl_route[0].a_device_id
            })

    @api.depends('epl_route.z_device_id')
    def compute_epl_route_last_device_id(self):
        for rec in self:
            if not rec.epl_route:
                continue
            rec.update({
                'epl_route_last_device_id': rec.epl_route[-1].z_device_id
            })

    @api.depends('epl_route.latency')
    def compute_epl_route_latency(self):
        for rec in self:
            rec.update({
                'epl_route_latency': sum(rec.mapped('epl_route.latency'))
            })

    @api.depends('epl_route.mrc_mb')
    def compute_epl_route_mrc_mb(self):
        for rec in self:
            rec.update({
                'epl_route_mrc_mb': sum(rec.mapped('epl_route.mrc_mb'))
            })

    @api.depends('epl_route.mrr_mb')
    def compute_epl_route_mrr_mb(self):
        for rec in self:
            rec.update({
                'epl_route_mrr_mb': sum(rec.mapped('epl_route.mrr_mb'))
            })

    @api.depends('epl_route_mrc_mb', 'epl_bandwidth')
    def compute_epl_route_mrc(self):
        for rec in self:
            rec.update({
                'epl_route_mrc': rec.epl_route_mrc_mb * rec.epl_bandwidth
            })

    @api.depends('epl_route_mrr_mb', 'epl_bandwidth')
    def compute_epl_route_mrr(self):
        for rec in self:
            rec.update({
                'epl_route_mrr': rec.epl_route_mrr_mb * rec.epl_bandwidth
            })

    # EPL BACKUP COMPUTES

    @api.depends('epl_backup.a_device_id')
    def compute_epl_backup_first_device_id(self):
        for rec in self:
            if not rec.epl_backup:
                continue
            rec.update({
                'epl_backup_first_device_id': rec.epl_backup[0].a_device_id
            })

    @api.depends('epl_backup.z_device_id')
    def compute_epl_backup_last_device_id(self):
        for rec in self:
            if not rec.epl_backup:
                continue
            rec.update({
                'epl_backup_last_device_id': rec.epl_backup[-1].z_device_id
            })

    @api.depends('epl_backup.latency')
    def compute_epl_backup_latency(self):
        for rec in self:
            rec.update({
                'epl_backup_latency': sum(rec.mapped('epl_backup.latency'))
            })

    @api.depends('epl_backup.mrc_mb', 'epl_backup_discount')
    def compute_epl_backup_mrc_mb(self):
        for rec in self:
            backup_mrc_mb = sum(rec.mapped('epl_backup.mrc_mb'))
            backup_mrc_mb *= (1 - rec.epl_backup_discount / 100.0)
            rec.update({
                'epl_backup_mrc_mb': backup_mrc_mb
            })

    @api.depends('epl_backup.mrr_mb', 'epl_backup_discount')
    def compute_epl_backup_mrr_mb(self):
        for rec in self:
            backup_mrr_mb = sum(rec.mapped('epl_backup.mrr_mb'))
            backup_mrr_mb *= (1 - rec.epl_backup_discount / 100.0)
            rec.update({
                'epl_backup_mrr_mb': backup_mrr_mb
            })

    @api.depends('epl_backup_mrc_mb', 'epl_bandwidth')
    def compute_epl_backup_mrc(self):
        for rec in self:
            rec.update({
                'epl_backup_mrc': rec.epl_backup_mrc_mb * rec.epl_bandwidth
            })

    @api.depends('epl_backup_mrr_mb', 'epl_bandwidth')
    def compute_epl_backup_mrr(self):
        for rec in self:
            rec.update({
                'epl_backup_mrr': rec.epl_backup_mrr_mb * rec.epl_bandwidth
            })

    # EPL PRODUCTS COMPUTES

    @api.depends('epl_products.mrc')
    def compute_epl_products_mrc(self):
        for rec in self:
            rec.update({
                'epl_products_mrc': sum(rec.mapped('epl_products.mrc'))
            })

    @api.depends('epl_products.mrr')
    def compute_epl_products_mrr(self):
        for rec in self:
            rec.update({
                'epl_products_mrr': sum(rec.mapped('epl_products.mrr'))
            })

    @api.depends('epl_products_mrc', 'epl_bandwidth')
    def compute_epl_products_mrc_mb(self):
        for rec in self:
            if not rec.epl_bandwidth:
                continue
            rec.update({
                'epl_products_mrc_mb': rec.epl_products_mrc / rec.epl_bandwidth
            })

    @api.depends('epl_products_mrr', 'epl_bandwidth')
    def compute_epl_products_mrr_mb(self):
        for rec in self:
            if not rec.epl_bandwidth:
                continue
            rec.update({
                'epl_products_mrr_mb': rec.epl_products_mrr / rec.epl_bandwidth
            })

    @api.depends('epl_products.nrr')
    def compute_epl_products_nrr(self):
        for rec in self:
            rec.update({
                'epl_products_nrr': sum(rec.mapped('epl_products.nrr'))
            })

    # EPL PRICE & COST COMPUTES

    @api.depends('epl_route_mrc_mb', 'epl_backup_mrc_mb',
                 'epl_products_mrc_mb')
    def compute_epl_mrc_mb(self):
        for rec in self:
            epl_mrc_mb = rec.epl_route_mrc_mb \
                         + rec.epl_backup_mrc_mb \
                         + rec.epl_products_mrc_mb
            rec.update({
                'epl_mrc_mb': epl_mrc_mb
            })

    @api.depends('epl_route_mrr_mb', 'epl_backup_mrr_mb',
                 'epl_products_mrr_mb')
    def compute_epl_mrr_mb(self):
        for rec in self:
            epl_mrr_mb = rec.epl_route_mrr_mb \
                         + rec.epl_backup_mrr_mb \
                         + rec.epl_products_mrr_mb
            rec.update({
                'epl_mrr_mb': epl_mrr_mb
            })

    @api.depends('epl_mrc_mb', 'epl_bandwidth')
    def compute_epl_mrc(self):
        for rec in self:
            rec.update({
                'epl_mrc': rec.epl_mrc_mb * rec.epl_bandwidth
            })

    @api.depends('epl_mrr_mb', 'epl_bandwidth')
    def compute_dflt_epl_mrr(self):
        for rec in self:
            rec.update({
                'dflt_epl_mrr': rec.epl_mrr_mb * rec.epl_bandwidth
            })

    # EPL CONSTRAINTS

    # EPL LINKS MUST BE SUCCESSIVE
    # ROUTE & BACKUP PATHS MUST HAVE SAME START/END DEVICE
    @api.constrains('epl_route', 'epl_backup')
    def constraints_epl_route_backup(self):
        for rec in self:
            if not rec.is_epl:
                continue  # Constraints do not apply
            if not rec.epl_route:
                raise ValidationError(_("Missing Route Path"))
            self.validate_path(rec.epl_route, "Route")
            if not rec.epl_backup:
                continue
            self.validate_path(rec.epl_backup, "Backup")
            if rec.epl_backup_first_device_id != rec.epl_route_first_device_id:
                raise ValidationError(_("Different start device Route/Backup"))
            if rec.epl_backup_last_device_id != rec.epl_route_last_device_id:
                raise ValidationError(_("Different end device Route/Backup"))

    @api.model
    def validate_path(self, path, path_name):
        for i in xrange(1, len(path)):
            cur_link = path[i]
            prev_link = path[i - 1]
            if cur_link.a_device_id != prev_link.z_device_id:
                link_name = "%s -> %s" % (cur_link.a_device_id.name,
                                          cur_link.z_device_id.name)
                raise ValidationError(_("Unconsecutive %s Link %s"
                                        % (path_name, link_name)))

    # EPL BANDWIDTH MUST BE POSITIVE
    @api.constrains('epl_bandwidth')
    def constraints_epl_bandwidth(self):
        for rec in self:
            if not rec.is_epl:  # Constraints do not apply
                continue
            if rec.epl_bandwidth <= 0:
                raise ValidationError(_("Invalid Bandwidth"))

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('epl_products')
    def constraints_epl_products(self):
        for rec in self:
            if any(p.quantity < 0 for p in rec.epl_products):
                raise ValidationError(_("Negative quantity on Products"))

    # EPL ADD/SAVE

    @api.multi
    def button_epl_save(self):
        return self.bundle_save(self.epl_name,
                                self.epl_description,
                                self.epl_mrr,
                                self.epl_nrr)
