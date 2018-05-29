from odoo import models, fields, api


class BackboneLink(models.Model):
    _name = 'backbone.link'
    _inherit = ['mail.thread']
    _order = "name ASC"

    name = fields.Char(
        string='Name',
        compute='compute_name',
        store=True
    )
    a_device_id = fields.Many2one(
        string='Device A',
        comodel_name='backbone.device',
        required=True,
        track_visibility='onchange'
    )
    a_xco_id = fields.Many2one(
        string='XConnect A',
        comodel_name='backbone.xco',
        track_visibility='onchange'
    )
    z_device_id = fields.Many2one(
        string='Device Z',
        comodel_name='backbone.device',
        required=True,
        track_visibility='onchange'
    )
    z_xco_id = fields.Many2one(
        string='XConnect Z',
        comodel_name='backbone.xco',
        track_visibility='onchange'
    )
    circuit_id = fields.Char(
        string='Circuit ID',
        track_visibility='onchange'
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        domain=[('supplier', '=', True)],
        context={'default_supplier': True},
        track_visibility='onchange'
    )
    supplier_name = fields.Char(
        string='Supplier Name',
        track_visibility='onchange'
    )
    supplier_link_id = fields.Char(
        string='Supplier Link ID',
        track_visibility='onchange'
    )
    is_wireless = fields.Boolean(
        string='Is Wireless',
        track_visibility='onchange'
    )
    latency = fields.Float(
        string='Latency (ms)',
        digits=(7, 3),
        track_visibility='onchange'
    )
    latency_sla = fields.Float(
        string='Latency SLA (ms)',
        digits=(7, 3),
        track_visibility='onchange'
    )
    latency_live = fields.Float(
        string='Latency Live (ms)',
        digits=(7, 3),
        readonly=True
    )
    bandwidth = fields.Integer(
        string='Bandwidth (Mbps)',
        track_visibility='onchange'
    )
    bearer = fields.Integer(
        string='Bearer (Mbps)',
        track_visibility='onchange'
    )
    cable_system = fields.Char(
        string='Cable System',
        track_visibility='onchange'
    )
    is_protected = fields.Boolean(
        string='Is Protected',
        default=False,
        track_visibility='onchange'
    )
    cable_system_protection = fields.Char(
        string='Protection System',
        track_visibility='onchange'
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        track_visibility='onchange'
    )
    nrc = fields.Float(
        string='NRC',
        track_visibility='onchange'
    )
    mrc = fields.Float(
        string='MRC',
        track_visibility='onchange'
    )
    mrc_mb = fields.Float(
        string='MRC / Mb',
        compute='compute_mrc_mb',
        store=True
    )
    nrr = fields.Float(
        string='NRR',
        track_visibility='onchange'
    )
    mrr = fields.Float(
        string='MRR',
        track_visibility='onchange'
    )
    mrr_mb = fields.Float(
        string='MRR / Mb',
        compute='compute_mrr_mb',
        store=True
    )
    date_start = fields.Date(
        string='Billing Date',
        track_visibility='onchange'
    )
    date_end = fields.Date(
        string='Expiration Date',
        track_visibility='onchange'
    )
    auto_renewal = fields.Selection(
        string='Auto-Renewal',
        selection=[('monthly', 'Monthly'),
                   ('quarterly', 'Quarterly'),
                   ('yearly', 'Yearly')],
        track_visibility='onchange'
    )
    notes = fields.Text(
        string='Notes',
        track_visibility='onchange'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        track_visibility='onchange'
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
