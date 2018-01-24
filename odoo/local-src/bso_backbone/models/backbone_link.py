from odoo import models, fields, api


class BackboneLink(models.Model):
    _name = 'backbone.link'

    name = fields.Char(
        string='Name',
        compute='compute_name'
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
    partner_id = fields.Char(
        string='Supplier',
        required=True
    )
    latency = fields.Float(
        string='Latency (ms)',
        required=True
    )
    bandwidth = fields.Integer(
        string='Bandwidth (Mbps)',
        required=True
    )
    cable = fields.Char(
        string='Cable'
    )
    is_protected = fields.Boolean(
        string='Protected',
        default=False
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    cost_upfront = fields.Float(
        string='Cost Upfront',
    )
    cost_monthly = fields.Float(
        string='Cost Monthly',
        required=True
    )
    cost_monthly_per_mb = fields.Float(
        string='Cost Monthly / Mb',
        compute='compute_cost_monthly_per_mb'
    )
    price_upfront = fields.Float(
        string='Price Upfront'
    )
    price_monthly = fields.Float(
        string='Price Monthly',
        required=True
    )
    price_monthly_per_mb = fields.Float(
        string='Price Monthly / Mb',
        compute='compute_price_monthly_per_mb'
    )
    date_end = fields.Date(
        string='Expiration Date',
        required=True
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
    attachment_number = fields.Integer(
        string='Number of Attachments',
        compute='_compute_attachment_number'
    )

    @api.depends('a_device_id.name', 'z_device_id.name', 'latency',
                 'is_protected')
    def compute_name(self):
        for rec in self:
            link_name = "%s <-> %s @ %.2fms" % (rec.a_device_id.name,
                                                rec.z_device_id.name,
                                                rec.latency)
            if rec.is_protected:
                link_name += " (Protected)"
            rec.update({
                'name': link_name
            })

    @api.depends('cost_monthly', 'bandwidth')
    def compute_cost_monthly_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'cost_monthly_per_mb': rec.cost_monthly / rec.bandwidth
                })

    @api.depends('price_monthly', 'bandwidth')
    def compute_price_monthly_per_mb(self):
        for rec in self:
            if rec.bandwidth:
                rec.update({
                    'price_monthly_per_mb': rec.price_monthly / rec.bandwidth
                })

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'backbone.link'), ('res_id', 'in', self.ids)],
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
        res['domain'] = [('res_model', '=', 'backbone.link'),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'backbone.link',
                          'default_res_id': self.id}
        return res
