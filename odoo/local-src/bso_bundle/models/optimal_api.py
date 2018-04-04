from collections import defaultdict
from heapq import heappop, heappush
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OptimalAPI(models.Model):
    _inherit = 'bundle.details'

    epl_optimal_pop_a = fields.Many2one(
        string='POP A',
        comodel_name='backbone.pop'
    )
    epl_optimal_pop_z = fields.Many2one(
        string='POP Z',
        comodel_name='backbone.pop'
    )
    epl_optimal_optimize = fields.Selection(
        string='Optimize for',
        selection=[('latency', 'Latency'),
                   ('price', 'Price')],
        default='latency'
    )
    epl_optimal_wireless = fields.Boolean(
        string='Allow Wireless'
    )
    epl_optimal_protected = fields.Boolean(
        string='Include Backup'
    )

    @api.onchange('epl_optimal_pop_a', 'epl_optimal_pop_z',
                  'epl_optimal_optimize', 'epl_optimal_wireless',
                  'epl_optimal_protected')
    def onchange_epl_optimal(self):
        for rec in self:
            rec.update({
                'epl_route': [],
                'epl_backup': []
            })

            if not all((rec.epl_optimal_pop_a, rec.epl_optimal_pop_z,
                        rec.epl_optimal_optimize)):
                continue

            optimal = self.get_optimal(rec.epl_optimal_pop_a,
                                       rec.epl_optimal_pop_z,
                                       rec.epl_optimal_optimize,
                                       rec.epl_optimal_protected)

            rec.update({
                'epl_route': self._get_path_values(
                    optimal['start_device'],
                    optimal['path'],
                    is_epl_backup=False)
            })

            if optimal['backup']:
                rec.update({
                    'epl_backup': self._get_path_values(
                        optimal['start_device'],
                        optimal['backup'],
                        is_epl_backup=True)
                })

            if optimal['warnings']:
                return {
                    'warning': {
                        'message': _("\n".join(optimal['warnings']))}
                }

    @api.model
    def get_optimal(self, a_pop_id, z_pop_id, optimize, protected):
        """Return the optimal path between 2 POPs for the optimized variable.
        Return backup path if available/applicable
        Return warnings to be notified to the user if applicable"""

        # Warning to be displayed to the user if populated
        warnings = []

        # Graph of all device_ids with their connected links
        graph = self._get_graph()

        a_devices = self._get_devices(a_pop_id)  # Possible starting devices
        z_devices = self._get_devices(z_pop_id)  # Possible ending devices

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
            raise ValidationError(_("No path available between '%s' & '%s'"
                                    % (a_pop_id.name, z_pop_id.name)))

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
                warnings.append(
                    "No valid backup found for path: %s <-> %s" %
                    (optimal['start_device'].name,
                     optimal['end_device'].name))

        return {'start_device': optimal['start_device'],
                'end_device': optimal['end_device'],
                'path': optimal['path'],
                'backup': backup.get('path', []),
                'warnings': warnings}

    @api.model
    def _get_graph(self):
        """Dict of all links with their a & z device_id as keys"""
        graph = defaultdict(lambda: [])
        links = self.env['backbone.link'].search(self._get_domain())
        for link in links:
            graph[link.a_device_id.id].append(link)
            graph[link.z_device_id.id].append(link)
        return graph

    @api.model
    def _get_domain(self):
        domain = [
            ('bandwidth', '>=', self.epl_bandwidth),
            ('latency', '>', 0),
        ]
        if not self.epl_optimal_wireless:
            domain.append(('is_wireless', '=', False))
        return domain

    @api.model
    def _get_devices(self, pop_id):
        """Get all POP's devices"""
        devices = self.env['backbone.device'].search([
            ('pop_id', '=', pop_id.id)
        ])
        return list(devices)

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
            return link.currency_id.compute(
                from_amount=link.mrr_mb,
                to_currency=self.currency_id,
                round=False
            )
        raise ValidationError(_("Invalid optimize: %s" % optimize))

    @api.model
    def _get_path_values(self, start_device, path, is_epl_backup):
        values = []
        sequence = 0
        for link in path:
            end_device = self._get_end_device(link, start_device)
            values.append((0, 0, {
                'is_epl_backup': is_epl_backup,
                'sequence': sequence,
                'link_id': link.id,
                'a_device_id': start_device.id,
                'z_device_id': end_device.id,
            }))
            sequence += 1
            start_device = end_device
        return values

    @api.model
    def _get_end_device(self, link, start_device):
        """Return link's other side device"""
        if link.a_device_id.id == start_device.id:
            return link.z_device_id
        return link.a_device_id
