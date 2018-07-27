# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import fields, models, api
from . import mailchimp_client

_logger = logging.getLogger(__name__)


class MailchimpListSegment(models.Model):
    _name = "mailchimp.list.segment"
    _order = ' mailchimp_create_date DESC'

    _sql_constraints = [
        ('ref_unique', 'UNIQUE (mailchimp_ref)', 'segment already exists')
    ]
    mailchimp_create_date = fields.Datetime(
        string='Create Date',
        default=datetime.utcnow(),
        readonly=True
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    mailchimp_ref = fields.Integer(
        string="Mailchimp ID",
        readonly=True,
    )
    list_id = fields.Many2one(
        string="List",
        comodel_name="mailchimp.list",
        ondelete="cascade",
        required=True,
    )
    lead_ids = fields.Many2many(
        string="Leads",
        comodel_name="crm.lead",
    )

    campaign_ids = fields.One2many(
        string="Campaign",
        comodel_name="mailchimp.campaign",
        inverse_name="segment_id",
    )
    segment_count = fields.Integer(
        string='Total Audience',
        compute='compute_segment_count',
        store=True,
        readonly=1

    )

    @api.depends('lead_ids')
    def compute_segment_count(self):
        for rec in self:
            rec.update({
                'segment_count': len(rec.lead_ids)
            })

    def action_view_leads(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        action['domain'] = [('segment_ids', '=', self.id)]
        return action

    @api.model
    def create(self, values):
        record = super(MailchimpListSegment, self).create(values)
        client = self.env['mailchimp.client'].get_client()
        if 'mailchimp_ref' not in values:
            mailchimp_ref = record._create_segment(client)
            record.write({'mailchimp_ref': mailchimp_ref})
        return record

    def _create_segment(self, client):
        data = {
            "name": self.name,
            "static_segment": []
        }
        return client.lists.segments.create \
            (self.list_id.mailchimp_ref, data).get('id')

    @api.multi
    def write(self, values):
        self.ensure_one()
        client = self.env['mailchimp.client'].get_client()
        saved_leads = self.lead_ids
        record = super(MailchimpListSegment, self).write(values)
        if 'lead_ids' in values:
            remaining_lead_ids = values['lead_ids'][0][2]
            remaining_leads = self.env["crm.lead"].browse(remaining_lead_ids)
            unlinked_leads = saved_leads - remaining_leads
            members_to_remove = self.get_members(unlinked_leads)
            added_leads = remaining_leads - saved_leads
            members_to_add = self.get_members(added_leads)
            self._update_members(client, members_to_add, members_to_remove)
        if 'mailchimp_ref' in values:
            members_to_add = self.get_members(self.lead_ids)
            self._update_members(client, members_to_add, [])
        if 'name' in values:
            self._update_name(client)
        return record

    def _update_name(self, client):
        data = {
            "name": self.name,
        }
        return client.lists.segments.update(self.list_id.mailchimp_ref,
                                            self.mailchimp_ref,
                                            data)

    def get_members(self, lead_ids):
        members = []
        for lead in lead_ids:
            email_from = self.env['mailchimp.client'].get_lead_email(lead)
            members.append(email_from)
        return members

    @mailchimp_client.handle_segment_exceptions
    def _update_members(self, client, members_to_add, members_to_remove):
        data = {
            "members_to_remove": members_to_remove,
            "members_to_add": members_to_add,
        }
        return client.lists.segments.update_members(self.list_id.mailchimp_ref,
                                                    self.mailchimp_ref,
                                                    data)

