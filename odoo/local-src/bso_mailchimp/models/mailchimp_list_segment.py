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
        readonly=True

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
        if 'mailchimp_ref' in values:
            return record  # Values are coming from Mailchimp -> Don't update

        client = self.env['mailchimp.client'].get_client()
        mailchimp_ref = record._create_segment(client)
        record.write({'mailchimp_ref': mailchimp_ref})
        members_to_add = record.get_members(record.lead_ids)
        record._update_members(client, members_to_add, [])

        return record

    def _create_segment(self, client):
        data = {
            "name": self.name,
            "static_segment": []
        }
        return client.lists.segments.create(self.list_id.mailchimp_ref,
                                            data).get('id')

    @api.multi
    def write(self, values):
        client = self.env['mailchimp.client'].get_client()
        for rec in self:
            if 'mailchimp_ref' in values:
                continue  # Values are coming from Mailchimp
                # -> Don't update
            if 'lead_ids' in values:
                edited_segment = self.new(values)
                remaining_leads = edited_segment.lead_ids
                saved_leads = rec.lead_ids
                unlinked_leads = saved_leads - remaining_leads
                added_leads = remaining_leads - saved_leads
                members_to_remove = rec.get_members(unlinked_leads)
                members_to_add = rec.get_members(added_leads)
                rec._update_members(client, members_to_add, members_to_remove)
            if 'name' in values:
                rec._update_name(client, values)
        return super(MailchimpListSegment, self).write(values)

    def _update_name(self, client, values):
        data = {
            "name": values.get('name', self.name),
        }
        return client.lists.segments.update(
            self.list_id.mailchimp_ref, self.mailchimp_ref, data)

    def get_members(self, lead_ids):
        members = []
        for lead in lead_ids:
            email_from = self.env['mailchimp.client'].get_lead_email(lead)
            members.append(email_from)
        return members

    @mailchimp_client.handle_segment_exceptions
    def _update_members(self, client, members_to_add, members_to_remove):
        max_members = 500  # Mailchimp API max array
        len_members = max(len(members_to_add), len(members_to_remove))
        iterations = len_members / max_members + 1
        for i in xrange(iterations):
            lower = i * max_members
            upper = (i + 1) * max_members
            cur_members_to_add = members_to_add[lower:upper]
            cur_members_to_remove = members_to_remove[lower:upper]
            data = {
                "members_to_add": cur_members_to_add,
                "members_to_remove": cur_members_to_remove,
            }
            client.lists.segments.update_members(
                self.list_id.mailchimp_ref, self.mailchimp_ref, data)
