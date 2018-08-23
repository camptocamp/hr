# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

import psycopg2

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model_cr
    def init(self):
        super(CrmLead, self).init()
        try:
            self.env.cr.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS unique_email "
                "ON crm_lead (email_from) WHERE type='lead';"
            )
        except psycopg2.Error:
            _logger.exception('Error creating unique index on lead emails')

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
