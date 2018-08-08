# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    _sql_constraints = [
        ('email_unique', 'UNIQUE (email_from)', 'Email already exists')
    ]

    list_ids = fields.Many2many(
        string="Lists",
        relation='lead_list_rel',
        comodel_name="mailchimp.list",
    )
    segment_ids = fields.Many2many(
        string="Segments",
        comodel_name="mailchimp.list.segment",
    )
    sum_campaigns = fields.Integer(
        string="Sum campaigns",
        compute="_compute_sum_campaigns",
    )

    @api.multi
    def _compute_sum_campaigns(self):
        for record in self:
            record.sum_campaigns = len(record.segment_ids)

    def action_view_campaigns(self):
        self.ensure_one()
        action = self.env.ref(
            'bso_mailchimp.crm_mailchimp_campaign_action_specific').read()[0]
        action['domain'] = [('segment_id', 'in', self.segment_ids.ids)]
        return action

    @api.model
    def create(self, values):
        if values.get('email_from'):
            values['email_from'] = values['email_from'].lower().strip()
        return super(CrmLead, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('email_from'):
            values['email_from'] = values['email_from'].lower().strip()
        return super(CrmLead, self).write(values)
