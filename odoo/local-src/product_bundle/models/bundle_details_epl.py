from collections import defaultdict
from heapq import heappop, heappush
from odoo import api, fields, models, exceptions, _


class BundleDetailsEPL(models.Model):
    _inherit = 'bundle.details'

    # EPL VARIABLES

    epl_bundle_name = fields.Char(
        string="Bundle Name",
        default="EPL []"
    )
    epl_bandwidth = fields.Integer(
        string="Bandwidth (Mbps)",
        default=100
    )

    # EPL ROUTE VARIABLES

    epl_route = fields.One2many(
        string='Route Path',
        comodel_name='bundle.details.epl.link',
        inverse_name='bundle_details_id_epl_route'
    )
    epl_route_last_device = fields.Many2one(
        string='Route Last Device',
        comodel_name='epl.device',
        compute='compute_epl_route_last_device'
    )
    epl_route_latency = fields.Char(
        string='Route Latency',
        compute='compute_epl_route_latency'
    )
    epl_route_price_per_mb = fields.Float(
        string='Route Price per Mbps',
        compute='compute_epl_route_price_per_mb'
    )
    epl_route_cost_per_mb = fields.Float(
        string='Route Cost per Mbps',
        compute='compute_epl_route_cost_per_mb'
    )
    epl_route_price = fields.Float(
        string='Route Price',
        compute='compute_epl_route_price'
    )
    epl_route_cost = fields.Float(
        string='Route Cost',
        compute='compute_epl_route_cost'
    )

    # EPL BACKUP VARIABLES

    epl_backup = fields.One2many(
        string='Backup Path',
        comodel_name='bundle.details.epl.link',
        inverse_name='bundle_details_id_epl_backup'
    )
    epl_backup_last_device = fields.Many2one(
        string='Backup Last Device',
        comodel_name='epl.device',
        compute='compute_epl_backup_last_device'
    )
    epl_backup_latency = fields.Char(
        string='Backup Latency',
        compute='compute_epl_backup_latency'
    )
    epl_backup_discount = fields.Integer(
        string='Backup Discount (%)',
        default=50
    )
    epl_backup_price_per_mb = fields.Float(
        string='Backup Price per Mbps',
        compute='compute_epl_backup_price_per_mb'
    )
    epl_backup_cost_per_mb = fields.Float(
        string='Backup Cost per Mbps',
        compute='compute_epl_backup_cost_per_mb'
    )
    epl_backup_price = fields.Float(
        string='Backup Price',
        compute='compute_epl_backup_price'
    )
    epl_backup_cost = fields.Float(
        string='Backup Cost',
        compute='compute_epl_backup_cost'
    )

    # EPL PRODUCTS VARIABLES

    epl_products_bundle_id = fields.Many2one(
        string='Products Bundle',
        comodel_name='product.product'
    )
    epl_products_bundle_categ_id = fields.Many2one(
        related='epl_products_bundle_id.categ_id',
        readonly=True
    )
    epl_products = fields.One2many(
        string='Products',
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_id_epl'
    )
    epl_products_price = fields.Float(
        string='Products Price',
        compute='compute_epl_products_price'
    )
    epl_products_cost = fields.Float(
        string='Products Cost',
        compute='compute_epl_products_cost'
    )
    epl_products_price_per_mb = fields.Float(
        string='Products Price per Mbps',
        compute='compute_epl_products_price_per_mb'
    )
    epl_products_cost_per_mb = fields.Float(
        string='Products Cost per Mbps',
        compute='compute_epl_products_cost_per_mb'
    )

    # EPL BUNDLE PRICE & COST VARIABLES
    epl_bundle_discount = fields.Integer(
        string='Bundle Discount (%)',
        default=0
    )
    epl_bundle_price_per_mb = fields.Float(
        string='Bundle Price per Mbps',
        compute='compute_epl_bundle_price_per_mb',
        help=_('(Route Price + Backup Price + Products Price) / Bandwidth')
    )
    epl_bundle_cost_per_mb = fields.Float(
        string='Bundle Cost per Mbps',
        compute='compute_epl_bundle_cost_per_mb',
        help=_('(Route Cost + Backup Cost + Products Cost) / Bandwidth')
    )
    epl_bundle_price = fields.Float(
        string='Bundle MRR',
        compute='compute_epl_bundle_price',
        help=_('Route Price + Backup Price + Products Price')
    )
    epl_bundle_cost = fields.Float(
        string='Bundle MRC',
        compute='compute_epl_bundle_cost',
        help=_('Route Cost + Backup Cost + Products Cost')
    )
    epl_bundle_price_upfront = fields.Float(
        string='Bundle NRR',
        default=1500
    )

    # OPTIMAL API VARIABLES

    button_epl_optimal_clicked = fields.Boolean(
        string='Find Optimal Path'
    )
    epl_optimal_pop_a = fields.Many2one(
        string='POP A',
        comodel_name='epl.pop'
    )
    epl_optimal_pop_z = fields.Many2one(
        string='POP Z',
        comodel_name='epl.pop'
    )
    epl_optimal_optimize = fields.Selection(
        string='Optimize for',
        selection=[('latency', 'Latency'),
                   ('price', 'Price')],
        default='latency'
    )
    epl_optimal_protected = fields.Boolean(
        string='Include Backup',
        default=False
    )

    # EPL ONCHANGES

    @api.onchange('show_epl')
    def onchange_show_epl(self):
        for rec in self:
            if not rec.show_epl:
                continue
            epl_products_bundle_id = rec.bundle_id.epl_products_bundle_id
            rec.update({
                'epl_products_bundle_id': epl_products_bundle_id,
                'epl_products': [
                    (0, 0,
                     {'bundle_categ_id': epl_products_bundle_id.categ_id,
                      'product_id': p.product_id,
                      'quantity': p.quantity})
                    for p in epl_products_bundle_id.products
                ]
            })
            for bdp in rec.epl_products:
                bdp.onchange_product_id()  # Compute default price_per_unit

    @api.onchange('epl_route', 'epl_backup')
    def onchange_epl_route_backup(self):
        for rec in self:
            epl_bundle_name = "EPL"

            if rec.epl_backup:
                epl_bundle_name += " Protected"

            epl_bundle_name += " ["

            if rec.epl_route:
                a_pop_id = rec.epl_route[0].a_device_id.pop_id
                z_pop_id = rec.epl_route[-1].z_device_id.pop_id
                epl_bundle_name += "%s <-> %s @ %s" % (a_pop_id.name,
                                                       z_pop_id.name,
                                                       rec.epl_route_latency)
            epl_bundle_name += "]"

            rec.update({
                'epl_bundle_name': epl_bundle_name
            })

    @api.onchange('epl_bandwidth')
    def onchange_epl_bandwidth(self):
        for rec in self:
            if rec.epl_bandwidth < 10000:
                epl_bundle_price_upfront = 1500
            else:
                epl_bundle_price_upfront = 3000
            rec.update({
                'epl_bundle_price_upfront': epl_bundle_price_upfront
            })

    # EPL ROUTE COMPUTES

    @api.depends('epl_route.z_device_id')
    def compute_epl_route_last_device(self):
        for rec in self:
            if rec.epl_route:
                res = rec.epl_route[-1].z_device_id
                rec.update({
                    'epl_route_last_device': res
                })

    @api.depends('epl_route.latency')
    def compute_epl_route_latency(self):
        for rec in self:
            res = "%.2f ms" % sum(rec.mapped('epl_route.latency'))
            rec.update({
                'epl_route_latency': res
            })

    @api.depends('epl_route.price_per_mb')
    def compute_epl_route_price_per_mb(self):
        for rec in self:
            res = sum(rec.mapped('epl_route.price_per_mb'))
            rec.update({
                'epl_route_price_per_mb': res
            })

    @api.depends('epl_route.cost_per_mb')
    def compute_epl_route_cost_per_mb(self):
        for rec in self:
            res = sum(rec.mapped('epl_route.cost_per_mb'))
            rec.update({
                'epl_route_cost_per_mb': res
            })

    @api.depends('epl_route_price_per_mb', 'epl_bandwidth')
    def compute_epl_route_price(self):
        for rec in self:
            res = rec.epl_route_price_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_route_price': res
            })

    @api.depends('epl_route_cost_per_mb', 'epl_bandwidth')
    def compute_epl_route_cost(self):
        for rec in self:
            res = rec.epl_route_cost_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_route_cost': res
            })

    # EPL BACKUP COMPUTES

    @api.depends('epl_backup.z_device_id')
    def compute_epl_backup_last_device(self):
        for rec in self:
            if rec.epl_backup:
                res = rec.epl_backup[-1].z_device_id
                rec.update({
                    'epl_backup_last_device': res
                })

    @api.depends('epl_backup.latency')
    def compute_epl_backup_latency(self):
        for rec in self:
            res = "%.2f ms" % sum(rec.mapped('epl_backup.latency'))
            rec.update({
                'epl_backup_latency': res
            })

    @api.depends('epl_backup.price_per_mb', 'epl_backup_discount')
    def compute_epl_backup_price_per_mb(self):
        for rec in self:
            res = sum(rec.mapped('epl_backup.price_per_mb'))
            res *= self.get_factor_from_percent(rec.epl_backup_discount)
            rec.update({
                'epl_backup_price_per_mb': res
            })

    @api.depends('epl_backup.cost_per_mb', 'epl_backup_discount')
    def compute_epl_backup_cost_per_mb(self):
        for rec in self:
            res = sum(rec.mapped('epl_backup.cost_per_mb'))
            res *= self.get_factor_from_percent(rec.epl_backup_discount)
            rec.update({
                'epl_backup_cost_per_mb': res
            })

    @api.depends('epl_backup_price_per_mb', 'epl_bandwidth')
    def compute_epl_backup_price(self):
        for rec in self:
            res = rec.epl_backup_price_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_backup_price': res
            })

    @api.depends('epl_backup_cost_per_mb', 'epl_bandwidth')
    def compute_epl_backup_cost(self):
        for rec in self:
            res = rec.epl_backup_cost_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_backup_cost': res
            })

    # EPL PRODUCTS COMPUTES

    @api.depends('epl_products.price')
    def compute_epl_products_price(self):
        for rec in self:
            res = sum(rec.mapped('epl_products.price'))
            rec.update({
                'epl_products_price': res
            })

    @api.depends('epl_products.cost')
    def compute_epl_products_cost(self):
        for rec in self:
            res = sum(rec.mapped('epl_products.cost'))
            rec.update({
                'epl_products_cost': res
            })

    @api.depends('epl_products_price', 'epl_bandwidth')
    def compute_epl_products_price_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                res = rec.epl_products_price / rec.epl_bandwidth
                rec.update({
                    'epl_products_price_per_mb': res
                })

    @api.depends('epl_products_cost', 'epl_bandwidth')
    def compute_epl_products_cost_per_mb(self):
        for rec in self:
            if rec.epl_bandwidth:
                res = rec.epl_products_cost / rec.epl_bandwidth
                rec.update({
                    'epl_products_cost_per_mb': res
                })

    # EPL BUNDLE PRICE & COST COMPUTES

    @api.depends('epl_route_price_per_mb', 'epl_backup_price_per_mb',
                 'epl_products_price_per_mb', 'epl_bundle_discount')
    def compute_epl_bundle_price_per_mb(self):
        for rec in self:
            res = rec.epl_route_price_per_mb \
                  + rec.epl_backup_price_per_mb \
                  + rec.epl_products_price_per_mb
            res *= self.get_factor_from_percent(rec.epl_bundle_discount)
            rec.update({
                'epl_bundle_price_per_mb': res
            })

    @api.depends('epl_route_cost_per_mb', 'epl_backup_cost_per_mb',
                 'epl_products_cost_per_mb')
    def compute_epl_bundle_cost_per_mb(self):
        for rec in self:
            res = rec.epl_route_cost_per_mb \
                  + rec.epl_backup_cost_per_mb \
                  + rec.epl_products_cost_per_mb
            rec.update({
                'epl_bundle_cost_per_mb': res
            })

    @api.depends('epl_bundle_price_per_mb', 'epl_bandwidth')
    def compute_epl_bundle_price(self):
        for rec in self:
            res = rec.epl_bundle_price_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_bundle_price': res
            })

    @api.depends('epl_bundle_cost_per_mb', 'epl_bandwidth')
    def compute_epl_bundle_cost(self):
        for rec in self:
            res = rec.epl_bundle_cost_per_mb * rec.epl_bandwidth
            rec.update({
                'epl_bundle_cost': res
            })

    # OPTIMAL PATH API

    @api.onchange('button_epl_optimal_clicked')
    def onchange_button_epl_optimal_clicked(self):
        for rec in self:
            # Workaround to prevent function from running at startup
            if not rec.button_epl_optimal_clicked:
                continue
            rec.update({
                'button_epl_optimal_clicked': False,
                'epl_route': [],
                'epl_backup': []
            })

            warnings = []
            if not rec.epl_optimal_pop_a:
                warnings.append("Missing POP A")
            if not rec.epl_optimal_pop_z:
                warnings.append("Missing POP Z")
            if not rec.epl_optimal_optimize:
                warnings.append("Missing Optimization")

            if all((rec.epl_optimal_pop_a,
                    rec.epl_optimal_pop_z,
                    rec.epl_optimal_optimize)):

                optimal = self.get_optimal(rec.epl_optimal_pop_a,
                                           rec.epl_optimal_pop_z,
                                           rec.epl_optimal_optimize,
                                           rec.epl_optimal_protected)

                rec.update({
                    'epl_route': self.get_optimal_path_values(
                        optimal['start_device'],
                        optimal['path'])
                })
                warnings.append("Route Path updated")

                if optimal['backup']:
                    rec.update({
                        'epl_backup': self.get_optimal_path_values(
                            optimal['start_device'],
                            optimal['backup'])
                    })
                    warnings.append("Backup Path updated")

                warnings += optimal['warnings']

            return {
                'warning': {'message': _("\n".join(warnings))}  # Translation
            }

    @api.model
    def get_optimal_path_values(self, start_device, path):
        values = []
        sequence = 0
        for link in path:
            end_device = self._get_end_device(link, start_device)
            values.append((0, 0, {
                'sequence': sequence,
                'link_id': link.id,
                'a_device_id': start_device.id,
                'z_device_id': end_device.id,
            }))
            sequence += 1
            start_device = end_device
        return values

    @api.model
    def get_optimal(self, a_pop_id, z_pop_id, optimize, protected):
        """Return the optimal path between 2 POPs for the optimized variable.
        Return backup path if available/applicable
        Return warnings to be notified to the user if applicable"""

        # Warning to be displayed to the user if populated
        warnings = []

        a_devices = self._get_devices(a_pop_id)  # Possible starting devices
        z_devices = self._get_devices(z_pop_id)  # Possible ending devices

        # Graph of all device_ids with their connected links
        graph = self._get_graph()

        # Find optimal path by looping through potential starting devices
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
                _("No Route available between '%s' & '%s'" % (a_pop_id.name,
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
                    warnings.append(warning)
            else:  # No backup found: notify it to user
                warnings.append("No valid backup found for path: %s <-> %s" %
                                (optimal['start_device'].name,
                                 optimal['end_device'].name))

        return {'start_device': optimal['start_device'],
                'end_device': optimal['end_device'],
                'path': optimal['path'],
                'backup': backup.get('path', []),
                'warnings': warnings}

    @api.model
    def _get_devices(self, pop_id):
        """Get all POP's devices"""
        devices = self.env['epl.device'].search([
            ('pop_id', '=', pop_id.id)
        ])
        return list(devices)

    @api.model
    def _get_graph(self):
        """Dict of all links with their a & z device_id as keys"""
        graph = defaultdict(lambda: [])
        links = self.env['epl.link'].sudo().search([])
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
                next_cost = self._get_cost(next_link, optimize)
                new_cost = cur_cost + next_cost
                new_path = cur_path + (next_link,)

                heappush(route, (new_cost, new_path, next_device))
        return {}

    @api.model
    def _get_cost(self, link, optimize):
        if optimize == 'latency':
            return link.latency
        if optimize == 'price':
            return link.currency_id.sudo().compute(
                from_amount=link.price_per_mb,
                to_currency=self.currency_id,
                round=False
            )
        raise exceptions.ValidationError(_("Invalid optimize: %s" % optimize))

    @api.model
    def _get_end_device(self, link, start_device):
        """Return link's other side device"""
        if link.a_device_id.id == start_device.id:
            return link.z_device_id
        return link.a_device_id

    # EPL CONSTRAINTS

    # EPL LINKS MUST BE SUCCESSIVE
    # MAIN & BACKUP PATH MUST HAVE SAME START/END DEVICE
    @api.constrains('epl_route', 'epl_backup')
    def constraints_epl_route_backup(self):
        for rec in self:
            if not rec.show_epl:
                continue  # Constraints do not apply
            if not rec.epl_route:
                raise exceptions.ValidationError(_("Missing Route Path"))
            self.validate_path(rec.epl_route, "Route")
            if rec.epl_backup:
                self.validate_path(rec.epl_backup, "Backup")
                backup_first_device = rec.epl_backup[0].a_device_id
                backup_last_device = rec.epl_backup[-1].z_device_id

                route_first_device = rec.epl_route[0].a_device_id
                route_last_device = rec.epl_route[-1].z_device_id

                if backup_first_device != route_first_device:
                    raise exceptions.ValidationError(
                        _("Route & Backup do not start from same device"))
                if backup_last_device != route_last_device:
                    raise exceptions.ValidationError(
                        _("Route & Backup do not end on same device"))

    @api.model
    def validate_path(self, path, path_name):
        for i in xrange(1, len(path)):
            cur_link = path[i]
            prev_link = path[i - 1]
            if cur_link.a_device_id.id != prev_link.z_device_id.id:
                link_name = "%s -> %s" % (cur_link.a_device_id.name,
                                          cur_link.z_device_id.name)
                raise exceptions.ValidationError(
                    _("Invalid %s Path:\n"
                      "Link %s is not successive" % (path_name, link_name)))

    # EPL BANDWIDTH MUST BE POSITIVE
    @api.constrains('epl_bandwidth')
    def constraints_epl_bandwidth(self):
        for rec in self:
            if not rec.show_epl:  # Constraints do not apply
                continue
            if rec.epl_bandwidth <= 0:
                raise exceptions.ValidationError(
                    _("EPL bandwidth must be a positive integer"))

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('epl_products')
    def constraints_epl_bundle_products(self):
        for rec in self:
            if not rec.show_epl:  # Constraints do not apply
                continue
            if any(p.quantity < 0 for p in rec.epl_products):
                raise exceptions.ValidationError(
                    _("Bundle products cannot contain negative quantities"))

    # EPL ADD/SAVE

    @api.multi
    def button_epl_save(self):
        return self.bundle_save(self.epl_products_bundle_id,
                                self.epl_bundle_name,
                                self.epl_bandwidth,
                                self.bundle_id.uom_id,
                                self.epl_bundle_price_per_mb,
                                self.epl_bundle_price_upfront)
