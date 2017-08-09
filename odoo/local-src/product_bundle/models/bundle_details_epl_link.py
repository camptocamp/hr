from openerp import api, fields, models


class BundleDetailsEPLLink(models.Model):
    _name = 'bundle.details.epl.link'

    sequence = fields.Integer(default=10)

    bundle_details_epl_id_route = fields.Many2one(
        string='Bundle Details EPL Route',
        comodel_name='bundle.details')

    bundle_details_epl_id_backup = fields.Many2one(
        string='Bundle Details EPL Backup',
        comodel_name='bundle.details')

    a_device_id = fields.Many2one(string="A Device",
                                  comodel_name='bso.network.device',
                                  required=True)

    z_device_id = fields.Many2one(string="Z Device",
                                  comodel_name='bso.network.device',
                                  required=True)

    link_id = fields.Many2one(string='Link',
                              comodel_name='bso.network.link',
                              required=True)

    a_pop_id = fields.Many2one(string='A POP',
                               comodel_name='bso.network.pop',
                               related='a_device_id.pop_id',
                               readonly=True)

    z_pop_id = fields.Many2one(string='Z POP',
                               comodel_name='bso.network.pop',
                               related='z_device_id.pop_id',
                               readonly=True)

    latency = fields.Float(string="Latency",
                           related='link_id.latency',
                           readonly=True)

    mrc = fields.Float(string="MRC",
                       related='link_id.mrc',
                       readonly=True)

    bandwidth = fields.Float(string="Bandwidth",
                             related='link_id.bandwith',
                             readonly=True)

    cablesystem_id = fields.Many2one(string="Cable",
                                     comodel_name='bso.network.cablesystem',
                                     related='link_id.cablesystem_id',
                                     readonly=True)

    mrc_bd = fields.Float(string="Price per MBps",
                          compute='_mrc_bd')

    @api.onchange('a_device_id')
    def set_domain_z_device_id(self):
        for rec in self:
            rec.z_device_id = False
            if not rec.a_device_id:
                continue
            links = self.get_link_ids(rec.a_device_id.id)
            device_keys = ('pop1_device_id', 'pop2_device_id')
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

    @api.model
    def get_link_ids(self, a_device_id, z_device_id=0):
        domain = ['|',
                  ('pop1_device_id', '=', a_device_id),
                  ('pop2_device_id', '=', a_device_id)]
        if z_device_id:
            domain += ['|',
                       ('pop1_device_id', '=', z_device_id),
                       ('pop2_device_id', '=', z_device_id)]
        return self.env['bso.network.link'].search(domain)

    @api.depends('link_id')
    def _mrc_bd(self):
        for rec in self:
            rec.mrc_bd = rec.mrc / rec.bandwidth
