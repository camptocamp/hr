from odoo import api, fields, models, exceptions, _
import math
from heapq import heappop, heappush
from collections import defaultdict


class BundleDetailsEPL(models.Model):
    _inherit = 'bundle.details'

    # EPL VISIBILITY
    epl_show = fields.Boolean(compute='_epl_show')

    # EPL BUNDLE_ID
    epl_bundle_id = fields.Many2one(string='EPL Bundle',
                                    comodel_name='product.product')

    # EPL BUNDLE CATEGORY
    epl_bundle_categ_id = fields.Many2one(string='Bundle Category',
                                          related='epl_bundle_id.categ_id',
                                          readonly=True)

    # POP A
    epl_a_pop = fields.Many2one(string='POP A',
                                comodel_name='epl.pop')

    # POP Z
    epl_z_pop = fields.Many2one(string='POP Z',
                                comodel_name='epl.pop')

    # OPTIMIZE FOR
    epl_optimize = fields.Selection(string="Optimize",
                                    selection=[('latency', 'Latency'),
                                               ('mrc_mb', 'Price')],
                                    default='latency')

    # FIND PROTECTION
    epl_protected = fields.Boolean(string='Protected')

    # EPL ROUTE
    epl_route = fields.One2many(string="EPL",
                                comodel_name='bundle.details.epl.link',
                                inverse_name='bundle_details_epl_id_route')

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
    epl_backup = fields.One2many(string="Backup",
                                 comodel_name='bundle.details.epl.link',
                                 inverse_name='bundle_details_epl_id_backup')

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
    epl_bundle_products = fields.One2many(
        string="Bundle Products",
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_epl_id')

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

    # EPL VISIBILITY FROM NAME
    @api.onchange('bundle_name')
    def _epl_show(self):
        """ hide classic bundle view if EPL """
        for rec in self:
            rec.epl_show = rec.bundle_name.lower() == "epl"
            rec.bundle_show = not rec.epl_show

    # EPL BUNDLE ID FROM VISIBILITY
    @api.onchange('epl_show')
    def _epl_bundle_id(self):
        for rec in self:
            if rec.epl_show:
                rec.epl_bundle_id = self.get_bundle_id("network")

    # EPL ROUTE/BACKUP FROM CONFIG
    @api.onchange('epl_a_pop', 'epl_z_pop', 'epl_optimize', 'epl_protected')
    def _epl_paths(self):
        for rec in self:
            if not all((rec.epl_a_pop, rec.epl_z_pop, rec.epl_optimize)):
                continue
            optimal_path = self.get_optimal_path(rec.epl_a_pop,
                                                 rec.epl_z_pop,
                                                 rec.epl_optimize,
                                                 rec.epl_protected)
            if optimal_path['warning']:
                return {'warning': {'message': optimal_path['warning']}}

    @api.model
    def get_epl_path_ids(self, route):
        """ Odoo ids from API response """
        route_vals = []
        if route:
            sequence = 0
            details = route.get('details', [])
            for detail in details:
                sequence += 10
                link_bso_id = detail['cost']['bso_backbone_id']
                a_device_id = self.get_epl_device(detail['equip_start'])
                z_device_id = self.get_epl_device(detail['equip_end'])
                link = self.get_epl_link(link_bso_id)
                if link:
                    route_vals.append((0, 0, {'sequence': sequence,
                                              'link_id': link.id,
                                              'a_device_id': a_device_id,
                                              'z_device_id': z_device_id}))
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
    @api.depends('epl_route')
    def _epl_route_price_per_mb(self):
        for rec in self:
            rec.epl_route_price_per_mb = sum(
                link.mrc_bd for link in rec.epl_route)

    # EPL ROUTE COST PER MBPs
    @api.depends('epl_route')
    def _epl_route_cost_per_mb(self):
        for rec in self:
            rec.epl_route_cost_per_mb = 0  # TODO

    # EPL ROUTE LATENCY FROM SUM OF LINKS
    @api.depends('epl_route')
    def _epl_route_latency(self):
        for rec in self:
            rec.epl_route_latency = "%.2f ms" % sum(
                link.latency for link in rec.epl_route)

    # EPL ROUTE LAST DEVICE
    @api.depends('epl_route')
    def _epl_route_last_device(self):
        for rec in self:
            rec.epl_route_last_device = rec.epl_route[-1].z_device_id \
                if rec.epl_route else False

    # EPL BACKUP PRICE PER MBPs
    @api.depends('epl_backup')
    def _epl_backup_price_per_mb(self):
        for rec in self:
            rec.epl_backup_price_per_mb = sum(
                link.mrc_bd for link in rec.epl_backup)

    # EPL BACKUP COST PER MBPs
    @api.depends('epl_backup')
    def _epl_backup_cost_per_mb(self):
        for rec in self:
            rec.epl_backup_cost_per_mb = 0  # TODO

    # EPL BACKUP LATENCY FROM SUM OF LINKS
    @api.depends('epl_backup')
    def _epl_backup_latency(self):
        for rec in self:
            rec.epl_backup_latency = "%.2f ms" % sum(
                link.latency for link in rec.epl_backup)

    # EPL BACKUP LAST DEVICE
    @api.depends('epl_backup')
    def _epl_backup_last_device(self):
        for rec in self:
            rec.epl_backup_last_device = rec.epl_backup[-1].z_device_id \
                if rec.epl_backup else False

    # EPL PRICE PER Mbps FROM ROUTE & BACKUP
    @api.depends('epl_route_price_per_mb', 'epl_backup_price_per_mb')
    def _epl_price_per_mb(self):
        for rec in self:
            epl_price_per_mb = rec.epl_route_price_per_mb \
                               + rec.epl_backup_price_per_mb * 0.5
            rec.epl_price_per_mb = self.round_upper_decimal(epl_price_per_mb)

    # EPL COST PER Mbps FROM ROUTE & BACKUP
    @api.depends('epl_route_cost_per_mb', 'epl_backup_cost_per_mb')
    def _epl_cost_per_mb(self):
        for rec in self:
            rec.epl_cost_per_mb = 0  # TODO

    # EPL PRICE FROM PRICE PER MBps & BANDWIDTH
    @api.depends('epl_price_per_mb', 'epl_bandwidth')
    def _epl_price(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_price = rec.epl_price_per_mb * rec.epl_bandwidth

    # EPL COST FROM COST PER MBps & BANDWIDTH
    @api.depends('epl_route_cost_per_mb', 'epl_backup_cost_per_mb')
    def _epl_cost(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_cost = rec.epl_cost_per_mb * rec.epl_bandwidth

    # EPL DESCRIPTION FROM EPL ROUTE
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
    @api.onchange('epl_show')
    def _epl_bundle_products(self):
        for rec in self:
            if not rec.epl_show:  # Do not display products
                continue
            rec.epl_bundle_products = [(0, 0, {'product_id': p.product_id,
                                               'product_quantity': p.quantity})
                                       for p in
                                       rec.epl_bundle_id.products]

    # EPL BUNDLE TOTAL PRICE FROM EPL BUNDLE PRODUCTS
    @api.depends('epl_bundle_products')
    def _epl_bundle_price(self):
        for rec in self:
            rec.epl_bundle_price = sum(
                p.product_total_price for p in rec.epl_bundle_products)

    # EPL BUNDLE PRICE PER MBps FROM EPL BUNDLE TOTAL PRICE & BANDWIDTH
    @api.depends('epl_bundle_price', 'epl_bandwidth')
    def _epl_bundle_price_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_bundle_price_per_mb = self.round_upper_decimal(
                    rec.epl_bundle_price / rec.epl_bandwidth)

    # EPL BUNDLE TOTAL COST FROM EPL BUNDLE PRODUCTS
    @api.depends('epl_bundle_products')
    def _epl_bundle_cost(self):
        for rec in self:
            rec.epl_bundle_cost = sum(
                p.product_total_cost for p in rec.epl_bundle_products)

    # EPL BUNDLE COST PER MBps FROM EPL BUNDLE TOTAL COST & BANDWIDTH
    @api.depends('epl_bundle_cost', 'epl_bandwidth')
    def _epl_bundle_cost_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_bundle_cost_per_mb = self.round_upper_decimal(
                    rec.epl_bundle_cost / rec.epl_bandwidth)

    # EPL PRICE PER MBps INCLUDING EPL BUNDLE PRICE PER MBps
    @api.depends('epl_price_per_mb', 'epl_bundle_price_per_mb')
    def _epl_total_price_per_mb(self):
        for rec in self:
            rec.epl_total_price_per_mb = self.epl_price_per_mb \
                                         + self.epl_bundle_price_per_mb

    # EPL PRICE PER MBps INCLUDING EPL BUNDLE PRICE PER MBps
    @api.depends('epl_cost_per_mb', 'epl_bundle_cost_per_mb')
    def _epl_total_cost_per_mb(self):
        for rec in self:
            rec.epl_total_cost_per_mb = self.epl_cost_per_mb \
                                        + self.epl_bundle_cost_per_mb

    # TRUNCATE PRICE TO UPPER DECIMAL POINT
    @api.model
    def round_upper_decimal(self, x):
        precision = self.get_decimal_precision()
        factor = 10 ** precision
        return math.ceil(x * factor) / factor

    # GET DECIMAL PRECISION SETTINGS FOR PRODUCTS
    @api.model
    def get_decimal_precision(self):
        return self.env['decimal.precision'].search(
            [('name', '=', 'Product Price')]).digits

    # EPL TOTAL PRICE FROM PRICE PER MBps & BANDWIDTH
    @api.depends('epl_total_price_per_mb', 'epl_bandwidth')
    def _epl_total_price(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_total_price = rec.epl_total_price_per_mb \
                                      * rec.epl_bandwidth

    # EPL TOTAL COST FROM COST PER MBps & BANDWIDTH
    @api.depends('epl_total_cost_per_mb', 'epl_bandwidth')
    def _epl_total_cost(self):
        for rec in self:
            if rec.epl_bandwidth:
                rec.epl_total_cost = rec.epl_total_cost_per_mb \
                                     * rec.epl_bandwidth

    # EPL ROUTE LINKS MUST BE SUCCESSIVE
    @api.constrains('epl_route')
    def _epl_route_constraints(self):
        for rec in self:
            if not rec.epl_show:  # Constraints do not apply
                continue
            if not rec.epl_route:
                raise exceptions.ValidationError(
                    _("EPL route required"))
            if not self.is_valid_route(rec.epl_route):
                raise exceptions.ValidationError(
                    _("EPL route links are not successive"))

    # EPL BACKUP LINKS MUST BE SUCCESSIVE & MATCH MAIN ROUTE
    @api.constrains('epl_protected', 'epl_route', 'epl_backup')
    def _epl_backup_constraints(self):
        for rec in self:
            if not rec.epl_show:  # Constraints do not apply
                continue
            if not rec.epl_protected or not rec.epl_route:
                continue
            if not rec.epl_backup:
                raise exceptions.ValidationError(
                    _("EPL backup required if protection is selected"))
            if not self.is_valid_route(rec.epl_backup):
                raise exceptions.ValidationError(
                    _("EPL backup links are not successive"))

            backup_first_device = rec.epl_backup[0].a_device_id
            backup_last_device = rec.epl_backup[-1].z_device_id

            route_first_device = rec.epl_route[0].a_device_id
            route_last_device = rec.epl_route[-1].z_device_id

            if backup_first_device != route_first_device:
                raise exceptions.ValidationError(
                    _("EPL route & backup do not start from same device"))
            if backup_last_device != route_last_device:
                raise exceptions.ValidationError(
                    _("EPL route & backup do not end on same device"))

    @api.model
    def is_valid_route(self, route):
        for i in xrange(1, len(route)):
            start_device_id = route[i].a_device_id.id
            prev_device_id = route[i - 1].z_device_id.id
            if start_device_id != prev_device_id:
                return False
        return True

    # EPL BANDWIDTH MUST BE POSITIVE
    @api.constrains('epl_bandwidth')
    def _epl_bandwidth_constraints(self):
        for rec in self:
            if not rec.epl_show:  # Constraints do not apply
                continue
            if rec.epl_bandwidth <= 0:
                raise exceptions.ValidationError(
                    _("EPL bandwidth must be a positive integer"))

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('epl_bundle_products')
    def _epl_bundle_products_constraints(self):
        for rec in self:
            if not rec.epl_show:  # Constraints do not apply
                continue
            if any(p.product_quantity < 0 for p in
                   rec.epl_bundle_products):
                raise exceptions.ValidationError(
                    _("Bundle products cannot contain negative quantities"))

    # ADD EPL TO SALE ORDER
    @api.multi
    def button_epl_save(self):
        return self.sale_order_line_save(
            product=self.epl_bundle_id,
            description=self.epl_description,
            quantity=self.epl_bandwidth,
            unit_measure=self.bundle_id.uom_id,
            unit_price=self.epl_total_price_per_mb
        )

    # OPTIMAL PATH

    @api.model
    def get_optimal_path(self, a_pop_id, z_pop_id, optimize, protected):
        """Return the optimal path between 2 POPs for the optimized variable.
        Return backup path if exists and protection requested
        Return warnings to be notified to the user if applicable"""

        # Warning to be displayed to the user if populated
        warnings = []

        a_devices = self._get_devices(a_pop_id)  # Possible starting devices
        z_devices = self._get_devices(z_pop_id)  # Possible ending devices

        # Graph of all device_ids with their connected links
        graph = self._get_graph()

        # Find optimal path (loop trough starting devices to ensure fastest)
        optimal = {}
        for a_device in a_devices:
            potential = self._get_optimal_path(graph,
                                               a_device,
                                               z_devices,
                                               optimize)
            if not potential:
                continue
            if not optimal or potential['cost'] < optimal['cost']:
                optimal = potential

        # Raise error if no path found
        if not optimal:
            raise exceptions.ValidationError(
                _("No path available between '%s' & '%s'" % (a_pop_id.name,
                                                             z_pop_id.name)))

        # Find backup path if protection requested
        backup = {}
        if protected:
            # Exclude links used in optimal path except protected ones
            exclude_link_ids = list(link.id for link in optimal['path']
                                    if not link.is_protected)
            backup = self._get_optimal_path(graph,
                                            optimal['start_device'],
                                            [optimal['end_device']],
                                            optimize,
                                            exclude_link_ids)
            # Build Backup warnings to be displayed to user
            if backup:
                # Look for duplicates
                duplicates = set(optimal['path']) & set(backup['path'])
                for duplicate in duplicates:
                    # Duplicates found: notify it to user
                    warning = "Backup uses duplicate link %s" % duplicate.name
                    if duplicate.is_protected:
                        warning += " (Protected)"
                    warnings.append(warning)
            else:  # No backup found: notify it to user
                warnings.append("No valid backup found for path: %s <-> %s" %
                                (optimal['start_device'],
                                 optimal['end_device']))

        return {'path': optimal,
                'backup': backup,
                'warning': "\n".join(warnings)}

    @api.model
    def _get_devices(self, pop_id):
        """Get all POP's devices"""
        devices = self.env['epl.device'].search([
            ('pop_id', '=', pop_id.id)
        ])
        return list(devices)

    @api.model
    def _get_graph(self):
        """Dict of all links with their a & z side device_id as keys"""
        graph = defaultdict(lambda: [])
        links = self.env['epl.link'].search([])
        for link in links:
            graph[link.a_device_id.id].append(link)
            graph[link.z_device_id.id].append(link)
        return graph

    @api.model
    def _get_optimal_path(self, graph, start_device, end_devices, optimize,
                          exclude_link_ids=None):
        """Find the optimal path between a starting device and any devices"""
        # Start device cannot be in end devices
        if start_device in end_devices:
            end_devices.remove(start_device)
        if not end_devices:
            return {}

        exclude_link_ids = exclude_link_ids or []

        init_cost = 0
        init_path = ()

        route = [(init_cost, init_path, start_device)]
        while route:
            (cur_cost, cur_path, cur_device) = heappop(route)

            if cur_device in end_devices:
                return {'cost': cur_cost,
                        'path': cur_path,
                        'start_device': start_device,
                        'end_device': cur_device}

            if cur_path:
                # Get current link: discard if in exclude, add otherwise
                cur_link_id = cur_path[-1].id
                if cur_link_id in exclude_link_ids:
                    continue
                exclude_link_ids.append(cur_link_id)

            for next_link in graph[cur_device.id]:
                if next_link.id in exclude_link_ids:
                    continue
                next_device = self._get_end_device(next_link, cur_device)
                next_cost = getattr(next_link, optimize)
                new_cost = cur_cost + next_cost
                new_path = cur_path + (next_link,)

                heappush(route, (new_cost, new_path, next_device))
        return {}

    @api.model
    def _get_end_device(self, link, start_device):
        """Return link's other side device"""
        if link.a_device_id == start_device:
            return link.z_device_id
        return link.a_device_id
