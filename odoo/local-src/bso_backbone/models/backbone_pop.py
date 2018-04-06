from odoo import models, fields, api


class BackbonePop(models.Model):
    _name = 'backbone.pop'
    _order = "name ASC"

    name = fields.Char(
        required=True
    )
    code = fields.Char(
        string='Code'
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
    address = fields.Char(
        string='Address'
    )
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 8)
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(11, 8)
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency'
    )
    kva_mrc = fields.Float(
        string='KVA MRC'
    )
    rack_nrc = fields.Float(
        string='Rack NRC'
    )
    rack_mrc = fields.Float(
        string='Rack MRC'
    )
    xco_nrc = fields.Float(
        string='XCo NRC'
    )
    xco_mrc = fields.Float(
        string='XCo MRC'
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
