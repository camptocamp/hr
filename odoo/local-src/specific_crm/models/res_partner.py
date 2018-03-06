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
    def _create_lead(self):
        self.ensure_one()
        self.env['crm.lead'].create({
            'name': self.name,
            'partner_id': self.id,
            'user_id': self.env.user.id,
        })

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('customer'):
            res._create_lead()
        return res

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if vals.get('customer'):
            for record in self:
                if len(record.lead_id) == 0:
                    self._create_lead()
        return res
