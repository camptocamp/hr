# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CreateCampaignWizard(models.TransientModel):
    _name = "create.campaign.wizard"

    def _default_lead_ids(self):
        return self.env['crm.lead'].browse(
            self.env.context.get('active_ids', False)
        )

    lead_ids = fields.Many2many(
        string="Leads",
        comodel_name="crm.lead",
        default=lambda self: self._default_lead_ids()
    )
    lead_count = fields.Integer(
        string="Lead count",
        compute="_compute_lead_count",
    )
    campaign_id = fields.Many2one(
        string="Campaign",
        comodel_name="crm.mailchimp.campaign",
        required=True,
    )
    new_mailing = fields.Boolean(
        string="Create New Mailing",
    )
    mailing_name = fields.Char(
        string="Mailing Name",
    )
    mailing_id = fields.Many2one(
        string="Mailing Name",
        comodel_name="crm.mailchimp.mailing",
        domain="[('campaign_id', '=', campaign_id)]",
    )

    @api.multi
    @api.depends("lead_ids")
    def _compute_lead_count(self):
        for record in self:
            if record.lead_ids:
                record.lead_count = len(record.lead_ids.filtered(
                    lambda x: x.type == "lead"
                ))

    @api.multi
    def action_create_mailing(self):
        self.ensure_one()
        if 'opportunity' in self.lead_ids.mapped('type'):
            raise ValidationError(_("""Some opportunities were selected.
            Only Leads can be added to a marketing campaign"""))
        if self.new_mailing:
            self._create_mailing()
        else:
            self._update_mailing()

    def _create_mailing(self):
        mailing = self.env['crm.mailchimp.mailing']
        leads = [(4, lead.id, 0) for lead in self.lead_ids]
        mailing = mailing.create({
            'name': self.mailing_name,
            'mailchimp_list': self.mailing_name,
            'campaign_id': self.campaign_id.id,
            'lead_ids': leads,
        })
        return mailing

    def _update_mailing(self):
        mailing = self.mailing_id
        leads = [(4, lead.id, 0) for lead in self.lead_ids]
        mailing.update({
            'lead_ids': leads,
        })
