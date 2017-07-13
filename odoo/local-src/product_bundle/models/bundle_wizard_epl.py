from openerp import api, fields, models, exceptions
import math


class BundleWizardEPL(models.Model):
    _inherit = 'bundle.wizard'

    # EPL VISIBILITY
    epl_show = fields.Boolean(compute='_epl_show',
                              default=False)

    # EPL BUNDLE_ID
    epl_bundle_id = fields.Many2one(string='Bundle',
                                    comodel_name='product.product')

    # POP A
    epl_a_pop = fields.Many2one(string='POP A',
                                comodel_name='bso.network.pop')

    # POP Z
    epl_z_pop = fields.Many2one(string='POP Z',
                                comodel_name='bso.network.pop')

    # OPTIMIZE FOR
    epl_sort = fields.Selection(string="Optimize",
                                selection=[(1, 'Latency'),
                                           (2, 'Price')],
                                default=1)

    # FIND PROTECTION
    epl_protected = fields.Boolean(string='Protected')

    # EPL ROUTE
    epl_route = fields.Many2many(string="EPL",
                                 comodel_name='bundle.wizard.epl.link',
                                 domain=[('is_backup', '=', False)])

    # EPL ROUTE PRICE PER MBps
    epl_route_price_per_mb = fields.Float(string="Route price per Mbps",
                                          compute='_epl_route_price_per_mb')

    # EPL ROUTE COST PER MBps
    epl_route_cost_per_mb = fields.Float(string="Route cost per Mbps",
                                         compute='_epl_route_cost_per_mb')

    # EPL ROUTE LATENCY
    epl_route_latency = fields.Char(string="Latency",
                                    compute='_epl_route_latency')

    # EPL ROUTE LAST DEVICE
    epl_route_last_device = fields.Many2one(string='Route last device',
                                            comodel_name='bso.network.device',
                                            compute='_epl_route_last_device')

    # EPL BACKUP ROUTE
    epl_backup = fields.Many2many(string="Backup",
                                  comodel_name='bundle.wizard.epl.link',
                                  domain=[('is_backup', '=', True)])

    # EPL BACKUP PRICE PER MBps
    epl_backup_price_per_mb = fields.Float(string="Backup price per Mbps",
                                           compute='_epl_backup_price_per_mb')

    # EPL BACKUP COST PER MBps
    epl_backup_cost_per_mb = fields.Float(string="Backup cost per Mbps",
                                          compute='_epl_backup_cost_per_mb')

    # BACKUP LATENCY
    epl_backup_latency = fields.Char(string="Backup Latency",
                                     compute='_epl_backup_latency')

    # BACKUP LAST DEVICE
    epl_backup_last_device = fields.Many2one(string='Backup last device',
                                             comodel_name='bso.network.device',
                                             compute='_epl_backup_last_device')

    # EPL PRODUCTS
    epl_bundle_products = fields.Many2many(string="Bundle Products",
                                           comodel_name='bundle.product')

    # EPL DESCRIPTION
    epl_description = fields.Char(string="Name",
                                  default="EPL []")

    # EPL PRICE PER MBps
    epl_price_per_mb = fields.Float(string="EPL Price per Mbps",
                                    compute='_epl_price_per_mb')

    # EPL COST PER MBps
    epl_cost_per_mb = fields.Float(string="EPL Cost per Mbps",
                                   compute='_epl_cost_per_mb')

    # EPL PRICE
    epl_price = fields.Float(string="EPL Price",
                             compute='_epl_price')

    # EPL COST
    epl_cost = fields.Float(string="EPL Cost",
                            compute='_epl_cost')

    # EPL BANDWIDTH
    epl_bandwidth = fields.Integer(string="Bandwidth")

    # EPL BUNDLE PRICE
    epl_bundle_price = fields.Float(string="Bundle Price",
                                    compute='_epl_bundle_price')

    # EPL BUNDLE COST
    epl_bundle_cost = fields.Float(string="Bundle Cost",
                                   compute='_epl_bundle_cost')

    # EPL BUNDLE PRICE PER MBps
    epl_bundle_price_per_mb = fields.Float(string="Bundle Price per MBps",
                                           compute='_epl_bundle_price_per_mb')

    # EPL BUNDLE COST PER MBps
    epl_bundle_cost_per_mb = fields.Float(string="Bundle Cost per MBps",
                                          compute='_epl_bundle_cost_per_mb')

    # EPL TOTAL PRICE PER MBps
    epl_total_price_per_mb = fields.Float(string="Total Price per MBps",
                                          compute='_epl_total_price_per_mb')

    # EPL TOTAL COST PER MBps
    epl_total_cost_per_mb = fields.Float(string="Total Cost per MBps",
                                         compute='_epl_total_cost_per_mb')

    # EPL TOTAL PRICE
    epl_total_price = fields.Float(string="Total Price",
                                   compute='_epl_total_price')

    # EPL TOTAL COST
    epl_total_cost = fields.Float(string="Total Cost",
                                  compute='_epl_total_cost')

    # GENERIC GET EPL PRODUCT
    @api.model
    def get_epl_product(self):
        return self.env['product.product'].search(
            [('name', '=ilike', "EPL"), ('is_epl', '=', True)])

    # EPL VISIBILITY FROM NAME
    @api.multi
    @api.onchange('bundle_name')
    def _epl_show(self):
        """ hide classic bundle view if EPL """
        for rec in self:
            rec.epl_show = rec.bundle_name.lower() == "epl"
            rec.bundle_show = not rec.epl_show

    # EPL BUNDLE ID FROM VISIBILITY
    @api.multi
    @api.onchange('epl_show')
    def _epl_bundle_id(self):
        for rec in self:
            if rec.epl_show:
                rec.epl_bundle_id = self.get_bundle_id("network")

    # EPL ROUTE/BACKUP FROM CONFIG
    @api.multi
    @api.onchange('epl_a_pop', 'epl_z_pop', 'epl_sort', 'epl_protected')
    def _epl_paths(self):
        for rec in self:
            if all((rec.epl_a_pop, rec.epl_z_pop, rec.epl_sort)):  # Config OK
                """ Fetching from API Latency """
                epl = self.env.user.company_id.network_api_id.call(
                    rec.epl_a_pop.name,
                    rec.epl_z_pop.name,
                    self.env.user,
                    backup=int(bool(rec.epl_protected)),
                    details=1,
                    sort=rec.epl_sort)
                rec.epl_route = self.get_epl_path_ids(epl.get('route'),
                                                      is_backup=False)
                rec.epl_backup = self.get_epl_path_ids(epl.get('backup'),
                                                       is_backup=True)

    @api.model
    def get_epl_path_ids(self, route, is_backup):
        """ Odoo ids from API response """
        route_vals = []
        if route:
            details = route.get('details', [])
            for detail in details:
                link_bso_id = detail['cost']['bso_backbone_id']
                a_device_id = self.get_epl_device(detail['equip_start'])
                z_device_id = self.get_epl_device(detail['equip_end'])
                link = self.get_epl_link(link_bso_id)
                if link:
                    route_vals.append((0, 0, {'link_id': link.id,
                                              'a_device_id': a_device_id,
                                              'z_device_id': z_device_id,
                                              'is_backup': is_backup}))
        return route_vals

    @api.model
    def get_epl_device(self, name):
        """ Odoo device from name """
        return self.env['bso.network.device'].search(
            [('name', '=ilike', name)])

    @api.model
    def get_epl_link(self, bso_id):
        """ Odoo link from bso_id """
        return self.env['bso.network.link'].search([('bso_id', '=', bso_id)])

    # EPL ROUTE PRICE PER MBPs
    @api.multi
    @api.depends('epl_route')
    def _epl_route_price_per_mb(self):
        for rec in self:
            rec.epl_route_price_per_mb = sum(
                link.mrc_bd for link in rec.epl_route)

    # EPL ROUTE COST PER MBPs
    @api.multi
    @api.depends('epl_route')
    def _epl_route_cost_per_mb(self):
        for rec in self:
            rec.epl_route_cost_per_mb = 0

    # EPL ROUTE LATENCY FROM SUM OF LINKS
    @api.multi
    @api.depends('epl_route')
    def _epl_route_latency(self):
        for rec in self:
            rec.epl_route_latency = "%.2f ms" % sum(
                link.latency for link in rec.epl_route)

    # EPL ROUTE LAST DEVICE
    @api.multi
    @api.depends('epl_route')
    def _epl_route_last_device(self):
        for rec in self:
            if rec.epl_route:
                rec.epl_route_last_device = rec.epl_route[-1].z_device_id
            else:
                rec.epl_route_last_device = False

    # EPL BACKUP PRICE PER MBPs
    @api.multi
    @api.depends('epl_backup')
    def _epl_backup_price_per_mb(self):
        for rec in self:
            rec.epl_backup_price_per_mb = sum(
                link.mrc_bd for link in rec.epl_backup)

    # EPL BACKUP COST PER MBPs
    @api.multi
    @api.depends('epl_backup')
    def _epl_backup_cost_per_mb(self):
        for rec in self:
            rec.epl_backup_cost_per_mb = 0

    # EPL BACKUP LATENCY FROM SUM OF LINKS
    @api.multi
    @api.depends('epl_backup')
    def _epl_backup_latency(self):
        for rec in self:
            rec.epl_backup_latency = "%.3f ms" % sum(
                link.latency for link in rec.epl_backup)

    # EPL ROUTE LAST DEVICE
    @api.multi
    @api.depends('epl_backup')
    def _epl_backup_last_device(self):
        for rec in self:
            rec.epl_backup_last_device = False
            if rec.epl_backup:
                rec.epl_backup_last_device = rec.epl_backup[-1].z_device_id

    # EPL PRICE PER Mbps FROM ROUTE & BACKUP
    @api.multi
    @api.depends('epl_route_price_per_mb', 'epl_backup_price_per_mb')
    def _epl_price_per_mb(self):
        for rec in self:
            epl_price_per_mb = rec.epl_route_price_per_mb \
                               + rec.epl_backup_price_per_mb * 0.5
            rec.epl_price_per_mb = self.round_upper_decimal(epl_price_per_mb)

    # EPL COST PER Mbps FROM ROUTE & BACKUP
    @api.multi
    @api.depends('epl_route_cost_per_mb', 'epl_backup_cost_per_mb')
    def _epl_cost_per_mb(self):
        for rec in self:
            rec.epl_cost_per_mb = 0

    # EPL PRICE FROM PRICE PER MBps & BANDWIDTH
    @api.multi
    @api.depends('epl_price_per_mb', 'epl_bandwidth')
    def _epl_price(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_price = rec.epl_price_per_mb * rec.epl_bandwidth

    # EPL COST FROM COST PER MBps & BANDWIDTH
    @api.multi
    @api.depends('epl_route_cost_per_mb', 'epl_backup_cost_per_mb')
    def _epl_cost(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_cost = rec.epl_cost_per_mb * rec.epl_bandwidth

    # EPL DESCRIPTION FROM EPL ROUTE
    @api.multi
    @api.onchange('epl_route', 'epl_protected')
    def _epl__description(self):
        for rec in self:
            epl_desc = "EPL"

            if rec.epl_protected:
                epl_desc += " Protected"

            epl_desc += " ["

            if rec.epl_route:
                epl_a_pop = rec.epl_route[0].a_pop_id
                epl_z_pop = rec.epl_route[-1].z_pop_id
                epl_desc += "%s <-> %s @ %s" % (epl_a_pop.name,
                                                epl_z_pop.name,
                                                rec.epl_route_latency)
            epl_desc += "]"

            rec.epl_description = epl_desc

    # EPL PRODUCTS FROM NETWORK BUNDLE PRODUCTS
    @api.multi
    @api.onchange('epl_show')
    def _epl_bundle_products(self):
        for rec in self:
            if rec.epl_show:  # Display products
                rec.epl_bundle_products = [(0, 0, {'product_id': p.id,
                                                   'product_quantity': 0})
                                           for p in
                                           rec.epl_bundle_id.default_products]

    # EPL BUNDLE TOTAL PRICE FROM EPL BUNDLE PRODUCTS
    @api.multi
    @api.depends('epl_bundle_products')
    def _epl_bundle_price(self):
        for rec in self:
            rec.epl_bundle_price = sum(
                p.product_total_price for p in rec.epl_bundle_products)

    # EPL BUNDLE PRICE PER MBps FROM EPL BUNDLE TOTAL PRICE & BANDWIDTH
    @api.multi
    @api.depends('epl_bundle_price', 'epl_bandwidth')
    def _epl_bundle_price_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_bundle_price_per_mb = self.round_upper_decimal(
                    rec.epl_bundle_price / rec.epl_bandwidth)

    # EPL BUNDLE TOTAL COST FROM EPL BUNDLE PRODUCTS
    @api.multi
    @api.depends('epl_bundle_products')
    def _epl_bundle_cost(self):
        for rec in self:
            rec.epl_bundle_cost = sum(
                p.product_total_cost for p in rec.epl_bundle_products)

    # EPL BUNDLE COST PER MBps FROM EPL BUNDLE TOTAL COST & BANDWIDTH
    @api.multi
    @api.depends('epl_bundle_cost', 'epl_bandwidth')
    def _epl_bundle_cost_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_bundle_cost_per_mb = self.round_upper_decimal(
                    rec.epl_bundle_cost / rec.epl_bandwidth)

    # EPL PRICE PER MBps INCLUDING EPL BUNDLE PRICE PER MBps
    @api.multi
    @api.depends('epl_price_per_mb', 'epl_bundle_price_per_mb')
    def _epl_total_price_per_mb(self):
        for rec in self:
            rec.epl_total_price_per_mb = self.epl_price_per_mb \
                                         + self.epl_bundle_price_per_mb

    # EPL PRICE PER MBps INCLUDING EPL BUNDLE PRICE PER MBps
    @api.multi
    @api.depends('epl_cost_per_mb', 'epl_bundle_cost_per_mb')
    def _epl_total_cost_per_mb(self):
        for rec in self:
            rec.epl_total_cost_per_mb = self.epl_cost_per_mb \
                                        + self.epl_bundle_cost_per_mb

    # TRUNCATE PRICE TO UPPER DECIMAL POINT
    @api.model
    def round_upper_decimal(self, x):
        precision = self.get_decimal_precision()
        factor = int("1" + "0" * precision)
        return math.ceil(x * factor) / factor

    # GET DECIMAL PRECISION SETTINGS FOR PRODUCTS
    @api.model
    def get_decimal_precision(self):
        return self.env['decimal.precision'].search(
            [('name', '=', 'Product Price')]).digits

    # EPL TOTAL PRICE FROM PRICE PER MBps & BANDWIDTH
    @api.multi
    @api.depends('epl_total_price_per_mb', 'epl_bandwidth')
    def _epl_total_price(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_total_price = rec.epl_total_price_per_mb \
                                      * rec.epl_bandwidth

    # EPL TOTAL COST FROM COST PER MBps & BANDWIDTH
    @api.multi
    @api.depends('epl_total_cost_per_mb', 'epl_bandwidth')
    def _epl_total_cost(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_total_cost = rec.epl_total_cost_per_mb \
                                     * rec.epl_bandwidth

    # EPL ROUTE LINKS MUST BE SUCCESSIVE
    @api.multi
    @api.constrains('epl_route')
    def _epl_route_constraints(self):
        for rec in self:
            if not self.is_valid_path(rec.epl_route):
                raise exceptions.ValidationError("EPL route path invalid")

    # EPL BACKUP LINKS MUST BE SUCCESSIVE & MATCH MAIN ROUTE
    @api.multi
    @api.constrains('epl_backup')
    def _epl_backup_constraints(self):
        for rec in self:
            if rec.epl_protected:
                if not self.is_valid_path(rec.epl_backup):
                    raise exceptions.ValidationError("EPL backup path invalid")

                backup_first_device = rec.epl_backup[0].a_device_id
                backup_last_device = rec.epl_backup[-1].z_device_id

                route_first_device = rec.epl_route[0].a_device_id
                route_last_device = rec.epl_route[-1].z_device_id

                if backup_first_device != route_first_device \
                        or backup_last_device != route_last_device:
                    raise exceptions.ValidationError(
                        "EPL route & backup paths do not match")

    # GENERIC VALID PATH CHECKER
    @api.model
    def is_valid_path(self, path):
        path_length = len(path)
        if not path_length:
            return False
        for i in xrange(1, path_length):
            if path[i].a_device_id != path[i - 1].z_device_id:
                return False
        return True

    # EPL BANDWIDTH MUST BE POSITIVE
    @api.multi
    @api.constrains('epl_bandwidth')
    def _epl_bandwidth_constraints(self):
        for rec in self:
            if rec.epl_show:  # Constraints apply
                if rec.epl_bandwidth <= 0:
                    raise exceptions.ValidationError(
                        "EPL bandwidth must be a positive integer")

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.multi
    @api.constrains('epl_bundle_products')
    def _epl_bundle_products_constraints(self):
        for rec in self:
            if rec.epl_show:  # Constraints apply
                if any(p.product_quantity < 0 for p in
                       rec.epl_bundle_products):
                    raise exceptions.ValidationError(
                        "Bundle products cannot contain negative quantities")

    # ADD EPL TO SALE ORDER
    @api.multi
    def button_add_epl(self):
        self.env['sale.order.line'].create(
            {'order_id': self.env.context['active_id'],
             'product_id': self.get_bundle_id("network").id,
             'name': self.epl_description,
             'price_unit': self.epl_total_price_per_mb,
             'product_uom': self.get_epl_product().uom_id.id,
             'product_uom_qty': self.epl_bandwidth})
        return True
