# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from mailchimp3.helpers import get_subscriber_hash

from odoo import fields, models, api
from . import mailchimp_client

_logger = logging.getLogger(__name__)


class MailchimpList(models.Model):
    _name = "mailchimp.list"
    _order = ' mailchimp_create_date DESC'

    _sql_constraints = [
        ('ref_unique', 'UNIQUE (mailchimp_ref)', 'List already exists')
    ]

    def _default_from_name(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.from_name')

    def _default_from_email(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.from_email')

    def _default_permission_reminder(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.permission_reminder')

    def _default_language(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.language')

    def _default_email_type_option(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.email_type_option')

    mailchimp_create_date = fields.Datetime(
        string='Create Date',
        default=datetime.utcnow(),
        readonly=True
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    from_email = fields.Char(
        default=lambda self: self._default_from_email(),
        string="From Email",
        required=True,
        help="The default from email for campaigns sent to this list."
    )
    from_name = fields.Char(
        default=lambda self: self._default_from_name(),
        string="From Name",
        required=True,
        help="The default from name for campaigns sent to this list."
    )
    permission_reminder = fields.Char(
        default=lambda self: self._default_permission_reminder(),
        string="Permission reminder",
        required=True,
        help="The permission reminder for the list."
    )
    subject = fields.Char(
        string="Subject",
        required=True,
        help="The default subject line for campaigns sent to this list."
    )
    language = fields.Char(
        default=lambda self: self._default_language(),
        string="Language",
        required=True,
        help="The default language for this lists’s forms."
    )
    email_type_option = fields.Boolean(
        default=lambda self: self._default_email_type_option(),
        string="Email type option",
        required=True,
        help="Whether the list supports multiple formats for emails."
    )
    mailchimp_ref = fields.Char(
        string="Mailchimp ID ",
        readonly=True
    )
    opt_out_lead_ids = fields.Many2many(
        string="Opt-Out Leads",
        relation='opt_out_list_rel',
        comodel_name="crm.lead",
    )
    lead_ids = fields.Many2many(
        string="Leads",
        relation='lead_list_rel',
        comodel_name="crm.lead",
        domain="[('opt_out','=',False),\
        ('id','not in',opt_out_lead_ids and opt_out_lead_ids[0][2] or False)]"
    )
    list_count = fields.Integer(
        string='Total Audience',
        compute='compute_list_count',
        store=True,
        readonly=1
    )

    @api.depends('lead_ids')
    def compute_list_count(self):
        for rec in self:
            rec.update({
                'list_count': len(rec.lead_ids)
            })

    def action_view_leads(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        action['domain'] = [('list_ids', '=', self.id)]
        self._update_action_window_context()
        return action

    def _update_action_window_context(self):
        rec = self.env['ir.actions.act_window'].search(
            [('name', '=', 'Create Segment')],
            limit=1)
        rec.update({'context': {'default_list_id': self.id}})

    @api.model
    def create(self, values):
        record = super(MailchimpList, self).create(values)
        client = self.env['mailchimp.client'].get_client()
        if 'mailchimp_ref' in values:
            record._create_webhook(client)
            return record  # Values are coming from Mailchimp -> Don't update

        mailchimp_ref = record._create_list(client)
        record.write({'mailchimp_ref': mailchimp_ref})
        record._create_update_members(client, external_leads=False)
        record._create_webhook(client)

        return record

    def _create_list(self, client):
        conf = self.env['ir.config_parameter']
        data = {
            "name": self.name,
            "contact":
                {
                    "company": conf.get_param('mailchimp.company'),
                    "address1": conf.get_param('mailchimp.address'),
                    "city": conf.get_param('mailchimp.city'),
                    "state": conf.get_param('mailchimp.state'),
                    "zip": conf.get_param('mailchimp.zip'),
                    "country": conf.get_param('mailchimp.country')
                },
            "permission_reminder": self.permission_reminder,
            "campaign_defaults":
                {
                    "from_name": self.from_name,
                    "from_email": self.from_email,
                    "subject": self.subject,
                    "language": self.language
                },
            "email_type_option": self.email_type_option,
        }
        return client.lists.create(data).get('id')

    @api.multi
    def write(self, values):
        client = self.env['mailchimp.client'].get_client()
        for rec in self:
            if 'mailchimp_ref' in values:
                continue
                # Values are coming from Mailchimp -> Don't update
            fields_content = ['name', 'from_email', 'from_name',
                              'permission_reminder', 'language', 'subject']
            if any(key in values for key in fields_content):
                rec._update_content(client, values)
            if 'lead_ids' in values:
                edited_list = self.new(values)
                remaining_leads = edited_list.lead_ids
                saved_leads = rec.lead_ids
                added_leads = remaining_leads - rec.lead_ids
                unlinked_leads = saved_leads - remaining_leads
                for lead in unlinked_leads:
                    email = self.env['mailchimp.client'].get_lead_email(
                        lead)
                    subscriber_hash = get_subscriber_hash(email)
                    rec.delete_mailchimp_list_member(client,
                                                     subscriber_hash)
                if added_leads:
                    rec._create_update_members(client, added_leads)
        return super(MailchimpList, self).write(values)

    @mailchimp_client.handle_list_exceptions
    def delete_mailchimp_list_member(self, client, subscriber_hash):
        return client.lists.members.delete(list_id=self.mailchimp_ref,
                                           subscriber_hash=subscriber_hash)

    def _update_content(self, client, values):
        conf = self.env['ir.config_parameter']
        data = {
            "name": values.get('name', self.name),
            "contact":
                {
                    "company": conf.get_param('mailchimp.company'),
                    "address1": conf.get_param('mailchimp.address'),
                    "city": conf.get_param('mailchimp.city'),
                    "state": conf.get_param('mailchimp.state'),
                    "zip": conf.get_param('mailchimp.zip'),
                    "country": conf.get_param('mailchimp.country')
                },
            "permission_reminder": values.get('permission_reminder',
                                              self.permission_reminder),
            "campaign_defaults":
                {
                    "from_name": values.get('from_name', self.from_name),
                    "from_email": values.get('from_email', self.from_email),
                    "subject": values.get('subject', self.subject),
                    "language": values.get('language', self.language)
                },
            "email_type_option": values.get('email_type_option',
                                            self.email_type_option),
        }
        return client.lists.update(self.mailchimp_ref, data)

    def _create_update_members(self, client, external_leads):
        members = []
        if external_leads:
            lead_ids = external_leads
        else:
            lead_ids = self.lead_ids
        for lead in lead_ids:
            email_from = self.env['mailchimp.client'].get_lead_email(lead)
            member = {
                "email_address": email_from,
                "status": 'subscribed',
                "status_if_new": 'subscribed',
            }
            members.append(member)

        max_members = 500  # Mailchimp API max array
        iterations = len(members) / max_members + 1
        for i in xrange(iterations):
            lower = i * max_members
            upper = (i + 1) * max_members
            cur_members = members[lower:upper]
            data = {
                "members": cur_members,
                "update_existing": True
            }
            client.lists.update_members(self.mailchimp_ref, data)

    def _create_webhook(self, client):
        conf = self.env['ir.config_parameter']
        webhook_url = conf.get_param('mailchimp.webhook_url')
        if not webhook_url:
            return
        webhooks = client.lists.webhooks.all(list_id=self.mailchimp_ref)
        if webhook_url in [w.get('url') for w in webhooks.get('webhooks', [])]:
            return
        data = {
            "url": webhook_url,
            "events": {
                "subscribe": True,
                "unsubscribe": True,
                "campaign": True,
            },
            "sources": {
                "user": True,
                "admin": True,
                "api": False
            }
        }
        client.lists.webhooks.create(self.mailchimp_ref, data)
