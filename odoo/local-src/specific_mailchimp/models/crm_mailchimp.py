# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class CrmMailchimpCampaign(models.Model):
    _name = "crm.mailchimp.campaign"

    name = fields.Char(
        string="Name",
        required=True,
    )
    mailing_ids = fields.One2many(
        string="Mailings",
        comodel_name="crm.mailchimp.mailing",
        inverse_name="campaign_id",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
    )


class CrmMailchimpMailing(models.Model):
    _name = "crm.mailchimp.mailing"

    def _default_state(self):
        return self._state_selection()[0][0]

    name = fields.Char(
        string="Name",
        required=True,
    )
    campaign_id = fields.Many2one(
        string="Campaign",
        comodel_name="crm.mailchimp.campaign",
    )
    mailchimp_list = fields.Char(
        string="Mailchimp list",
        required=True,
    )
    state = fields.Selection(
        string="State",
        selection="_state_selection",
        default=lambda self: self._default_state(),
    )
    lead_ids = fields.Many2many(
        string="Leads",
        comodel_name="crm.lead",
        domain="[('type', '=', 'lead')]",
    )
    report_ids = fields.One2many(
        string="Reports",
        comodel_name="crm.mailchimp.mailing.stats",
        inverse_name="mailing_id",
        readonly=True,
    )

    def _state_selection(self):
        return [
            ('draft', 'Draft'),
            ('running', 'running'),
        ]

    def action_view_leads(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        action['domain'] = [('id', 'in', self.lead_ids.ids)]
        return action

    def action_view_stats(self):
        self.ensure_one()
        action = self.env.ref(
            'specific_mailchimp.crm_mailchimp_mailing_stats_action_specific'
        ).read()[0]
        action['domain'] = [('id', 'in', self.report_ids.ids)]
        return action

    @api.multi
    def action_export(self):
        """
        TODO
        """
        return

    @api.multi
    def action_fetch(self):
        """
        TODO
        """
        return


class CrmMailchimpMailingStats(models.Model):
    _name = "crm.mailchimp.mailing.stats"

    name = fields.Char(
        string="Name",
    )
    mailing_id = fields.Many2one(
        string="Mailing",
        comodel_name="crm.mailchimp.mailing",
        required=True,
    )
    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead",
        required=True,
    )
    campaign_id = fields.Many2one(
        related="mailing_id.campaign_id",
        readonly=True,
        store=True,
    )
    sent = fields.Datetime(
        string="Date sent"
    )
    recieved = fields.Datetime(
        string="Date recieved"
    )
    bounced = fields.Datetime(
        string="Date bounced"
    )
    clicked = fields.Datetime(
        string="Date clicked"
    )
    unsubscribed = fields.Datetime(
        string="Date unsubscribed"
    )
