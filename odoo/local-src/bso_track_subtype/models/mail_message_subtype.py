# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        domain="[('model_id', '=', res_model)]",
    )
    trigger_value = fields.Char(
        string='Trigger value'
    )
    group_ids = fields.Many2many(
        comodel_name='res.groups',
        string='Groups'
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners'
    )
    notify_existing_followers = fields.Boolean(
        string='Notify exiting followers')

    _sql_constraints = [
        ('field_id_trigger_value_unique', 'unique(field_id, trigger_value)',
         'field_id and trigger_value should be unique by subtype')
    ]

    @api.constrains('field_id')
    def check_field_tracked(self):
        if not self.res_model:
            return
        tracked_fields = self.env[self.res_model]._get_tracked_fields([])
        if self.field_id.name in tracked_fields.keys():
            raise ValidationError('This field is already tracked.')

    @api.multi
    def write(self, vals):
        result = super(MailMessageSubtype, self).write(vals)
        if vals.get('group_ids'):
            self._populate_partner_ids()
        return result

    @api.model
    def create(self, vals):
        rec = super(MailMessageSubtype, self).create(vals)
        rec._populate_partner_ids()
        return rec

    def _populate_partner_ids(self):
        for rec in self:
            rec.write({'partner_ids': [
                (4, pid) for pid in
                rec.mapped('group_ids.users.partner_id').ids]})
