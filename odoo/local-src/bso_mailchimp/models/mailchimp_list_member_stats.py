# -*- coding: utf-8 -*-


from odoo import fields, models


class MailchimpListMemberStats(models.Model):
    _name = "mailchimp.list.member.stats"
    _inherits = {'crm.lead': 'lead_id'}

    campaign_id = fields.Many2one(
        string="Campaign",
        comodel_name="mailchimp.campaign",
        required=True,
        ondelete="cascade"
    )
    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead",
        ondelete="cascade",
        required=True
    )
    sent = fields.Datetime(
        string="Date sent"
    )
    opened = fields.Datetime(
        string="Date opened"
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
