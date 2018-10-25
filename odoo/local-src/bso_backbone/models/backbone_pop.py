# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, exceptions, _


class BackbonePop(models.Model):
    _name = 'backbone.pop'
    _inherit = ['mail.thread']
    _order = "name ASC"

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)', 'Name already exists'),
        ('code_unique', 'UNIQUE (code)', 'Code already exists')
    ]

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

    @api.constrains('name')
    def check_name(self):
        settings = self.env['backbone.settings'].get()
        for rec in self:
            if not bool(re.findall(
                    '^%s-%s$' % (settings.regex_city, settings.regex_pop),
                    rec.name)):
                raise exceptions.ValidationError(
                    _('%s does not respect the naming convention') % rec.name
                )

    @api.constrains('code')
    def check_code(self):
        settings = self.env['backbone.settings'].get()
        for rec in self:
            if not rec.code:
                continue
            if not bool(
                    re.findall('^%s$' % settings.regex_pop_code, rec.code)):
                raise exceptions.ValidationError(
                    _('%s does not respect the naming convention') % rec.code
                )
