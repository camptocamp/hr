from odoo import models, fields, api


class BackboneXCO(models.Model):
    _name = 'backbone.xco'

    name = fields.Char(
        compute='compute_name',
        store=True
    )
    a_side = fields.Char(
        string='A Side',
        default='BSO',
        required=True
    )
    a_side_port_id = fields.Char(
        string='A Side Port ID'
    )
    z_side = fields.Char(
        string='Z Side',
        required=True
    )
    z_side_port_id = fields.Char(
        string='Z Side Port ID'
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
    xco_id = fields.Char(
        string='XConnect ID',
        required=True
    )
    used = fields.Boolean(
        string='Used',
        default=True
    )
    project_code = fields.Char(
        string='Project Code',
        # comodel_name='delivery.project'
    )
    xco_type = fields.Selection(
        string='Type',
        selection=[('backbone', 'Backbone'),
                   ('client', 'Client')],
        required=True
    )
    service_id = fields.Char(
        string='Client Service ID'
    )
    link_id = fields.Char(
        string='Backbone Link ID'
    )
    paid_by_bso = fields.Boolean(
        string='Paid by BSO'
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

    @api.depends('supplier_name', 'xco_id')
    def compute_name(self):
        for rec in self:
            rec.update({
                'name': "%s - %s" % (rec.supplier_name, rec.xco_id)
            })
