# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BackboneIX(models.Model):
    _name = 'backbone.ix'
    _inherit = ['mail.thread']
    _order = "name ASC"

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)', 'Name already exists'),
    ]

    name = fields.Char(
        string='Name',
        track_visibility='onchange',
        required=True,
    )
    city = fields.Char(
        string='City',
        track_visibility='onchange',
        required=True,
    )
    country = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        track_visibility='onchange',
        required=True,
    )
    pop_id = fields.Many2one(
        string='POP',
        comodel_name='backbone.pop',
        track_visibility='onchange',
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
