# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PartnerBinding(models.TransientModel):

    _inherit = 'crm.partner.binding'

    @api.model
    def default_get(self, fields):
        res = super(PartnerBinding, self).default_get(fields)
        if res.get('action') == 'create':
            res['action'] = 'nothing'
        return res

    action = fields.Selection([
        ('exist', 'Link to an existing customer'),
        ('nothing', 'Do not link to a customer')
    ])
