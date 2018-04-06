from odoo import models, fields, api


class BackboneLink(models.Model):
    _name = 'backbone.link'

    name = fields.Char(
        string='Name',
        compute='compute_name',
        store=True
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='backbone.device',
        required=True
    )
    a_xco_id = fields.Many2one(
        string='XConnect A',
        comodel_name='backbone.xco'
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='backbone.device',
        required=True
    )
    z_xco_id = fields.Many2one(
        string='XConnect Z',
        comodel_name='backbone.xco'
    )
    tnms_id = fields.Char(
        string='TNMS ID'
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        domain=[('supplier', '=', True)],
        context={'default_supplier': True}
    )
    supplier_name = fields.Char(
        string='Supplier Name'
    )
    supplier_link_id = fields.Char(
        string='Supplier Link ID'
    )
    is_wireless = fields.Boolean(
        string='Is Wireless'
    )
    latency = fields.Float(
        string='Latency (ms)',
        digits=(7, 3)
    )
    latency_sla = fields.Float(
        string='Latency SLA (ms)',
        digits=(7, 3)
    )
    bandwidth = fields.Integer(
        string='Bandwidth (Mbps)'
    )
    bearer = fields.Integer(
        string='Bearer (Mbps)'
    )
    cable_system = fields.Char(
        string='Cable System'
    )
    is_protected = fields.Boolean(
        string='Is Protected',
        default=False
    )
    cable_system_protection = fields.Char(
        string='Protection System'
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency'
    )
    nrc = fields.Float(
        string='NRC'
    )
    mrc = fields.Float(
        string='MRC'
    )
    mrc_mb = fields.Float(
        string='MRC / Mb',
        compute='compute_mrc_mb',
        store=True
    )
    nrr = fields.Float(
        string='NRR'
    )
    mrr = fields.Float(
        string='MRR'
    )
    mrr_mb = fields.Float(
        string='MRR / Mb',
        compute='compute_mrr_mb',
        store=True
    )
    date_start = fields.Date(
        string='Billing Date'
    )
    date_end = fields.Date(
        string='Expiration Date'
    )
    auto_renewal = fields.Selection(
        string='Auto-Renewal',
        selection=[('monthly', 'Monthly'),
                   ('quarterly', 'Quarterly'),
                   ('yearly', 'Yearly')]
    )
    notes = fields.Text(
        string='Notes'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # ATTACHMENTS

    attachment_number = fields.Integer(
        string='Number of Attachments',
        compute='_compute_attachment_number'
    )

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment = dict(
            (data['res_id'], data['res_id_count']) for data in attachment_data)
        for rec in self:
            rec.attachment_number = attachment.get(rec.id, 0)

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base',
                                                           'action_attachment')
        res['domain'] = [('res_model', '=', self._name),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': self._name,
                          'default_res_id': self.id}
        return res

    # COMPUTES

    @api.depends('a_device_id.name', 'z_device_id.name', 'latency',
                 'is_wireless', 'is_protected')
    def compute_name(self):
        for rec in self:
            link_name = "%s <-> %s @ %s ms" % (rec.a_device_id.name,
                                               rec.z_device_id.name,
                                               rec.latency)
            if rec.is_wireless:
                link_name += " (Wireless)"
            if rec.is_protected:
                link_name += " (Protected)"
            rec.update({
                'name': link_name
            })

    @api.depends('mrc', 'bandwidth')
    def compute_mrc_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'mrc_mb': rec.mrc / rec.bandwidth
                })

    @api.depends('mrr', 'bandwidth')
    def compute_mrr_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'mrr_mb': rec.mrr / rec.bandwidth
                })
