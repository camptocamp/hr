from odoo import models, fields, api


class BackboneXCO(models.Model):
    _name = 'backbone.xco'
    _inherit = ['mail.thread']
    _order = "name ASC"

    name = fields.Char(
        compute='compute_name',
        store=True
    )
    a_side = fields.Char(
        string='A Side',
        default='BSO',
        required=True,
        track_visibility='onchange'
    )
    a_side_port = fields.Char(
        string='A Side Port',
        track_visibility='onchange'
    )
    z_side = fields.Char(
        string='Z Side',
        required=True,
        track_visibility='onchange'
    )
    z_side_port = fields.Char(
        string='Z Side Port',
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
    xco_ref = fields.Char(
        string='XConnect ID',
        required=True,
        track_visibility='onchange'
    )
    used = fields.Boolean(
        string='Used',
        default=True,
        track_visibility='onchange'
    )
    project_code = fields.Char(
        string='Project Code',
        # comodel_name='delivery.project',
        track_visibility='onchange'
    )
    xco_type = fields.Selection(
        string='Type',
        selection=[('backbone', 'Backbone'),
                   ('client', 'Client')],
        required=True,
        track_visibility='onchange'
    )
    service_ref = fields.Char(
        string='Client Service ID',
        track_visibility='onchange'
    )
    link_ref = fields.Char(
        string='Backbone Link ID',
        track_visibility='onchange'
    )
    paid_by_bso = fields.Boolean(
        string='Paid by BSO',
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

    @api.depends('supplier_id.name', 'supplier_name', 'xco_ref')
    def compute_name(self):
        for rec in self:
            supplier_name = rec.supplier_id.name or rec.supplier_name
            rec.update({
                'name': "%s - %s" % (supplier_name, rec.xco_ref)
            })
