from odoo import models, fields, api


class BackbonePop(models.Model):
    _name = 'backbone.pop'
    _inherit = ['mail.thread']
    _order = "name ASC"

    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    code = fields.Char(
        string='Code',
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
    address = fields.Char(
        string='Address',
        track_visibility='onchange'
    )
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 8),
        track_visibility='onchange'
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(11, 8),
        track_visibility='onchange'
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        track_visibility='onchange'
    )
    kva_mrc = fields.Float(
        string='KVA MRC',
        track_visibility='onchange'
    )
    rack_nrc = fields.Float(
        string='Rack NRC',
        track_visibility='onchange'
    )
    rack_mrc = fields.Float(
        string='Rack MRC',
        track_visibility='onchange'
    )
    xco_nrc = fields.Float(
        string='XCo NRC',
        track_visibility='onchange'
    )
    xco_mrc = fields.Float(
        string='XCo MRC',
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
