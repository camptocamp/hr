# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    lead_id = fields.One2many(
        string="Connected lead",
        comodel_name="crm.lead",
        inverse_name="partner_id",
    )

    @api.multi
    def _create_or_update_lead(self):
        self.ensure_one()
        if not self.id:
            return
        lead = self.env['crm.lead'].search(
            [('partner_id', '=', self.id),
             ('type', '=', 'lead')]
        )
        values = {
            'partner_id': self.id,
            'user_id': self.env.user.id,
            'email_from': self.email,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'phone': self.phone,
            'mobile': self.mobile,
            'fax': self.fax,
            'function': self.function,
            'title': self.title.id,
            'partner_name': self.parent_id.name,
        }
        if not lead:
            values['type'] = "lead"
            values['name'] = self.name
            self.env['crm.lead'].create(values)
        else:
            lead.update(values)

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('customer'):
            res._create_or_update_lead()
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        for record in self:
            if record.customer or record.lead_id:
                record._create_or_update_lead()
        return res
