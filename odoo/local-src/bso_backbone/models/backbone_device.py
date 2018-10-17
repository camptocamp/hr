# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, exceptions, _


class BackboneDevice(models.Model):
    _name = 'backbone.device'
    _inherit = ['mail.thread']
    _order = "name ASC"

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)', 'Name already exists'),
    ]

    name = fields.Char(
        required=True,
        track_visibility='onchange'
    )
    pop_id = fields.Many2one(
        string='POP',
        comodel_name='backbone.pop',
        required=True,
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
            if not rec.pop_id:
                continue
            if not bool(
                    re.findall(
                        "^%s-%s$" % (rec.pop_id.name, settings.regex_device),
                        rec.name)):
                raise exceptions.ValidationError(
                    _('%s does not respect the naming convention') % rec.name)

    # @api.multi
    # def remove_space_from_device_name(self):
    #     devices = self.search([])
    #     if not devices:
    #         return
    #     for device in devices:
    #         device.write({'name': device.name.strip()})
    #
