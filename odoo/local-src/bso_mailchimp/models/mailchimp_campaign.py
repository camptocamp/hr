# -*- coding: utf-8 -*-

from datetime import datetime

import dateutil.parser

from odoo import models, fields, api


class MailchimpCampaign(models.Model):
    _name = "mailchimp.campaign"
    _order = 'mailchimp_create_date DESC'

    _sql_constraints = [
        ('ref_unique', 'UNIQUE (mailchimp_ref)', 'Campaign already exists')
    ]

    def _default_reply_to(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.reply_to')

    def _default_type(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mailchimp.type')

    name = fields.Char(
        string="Name",
        required=True,
    )
    subject_line = fields.Char(
        string="Subject line",
    )
    from_name = fields.Char(
        string="From Name",
    )
    reply_to = fields.Char(
        default=lambda self: self._default_reply_to(),
        string="Reply to",
    )
    type = fields.Selection(
        [
            ('regular', 'Regular'),
            ('plaintext', 'Plaintext'),
            ('absplit', 'Absplit'),
            ('rss', 'RSS'),
            ('variate', 'Variate'),
        ],
        default=lambda self: self._default_type(),
        string="Type",
        required=True
    )
    mailchimp_ref = fields.Char(
        string="Mailchimp ID",
        readonly=True,
    )
    list_id = fields.Many2one(
        string="List",
        comodel_name="mailchimp.list",
        required=True
    )
    segment_id = fields.Many2one(
        string="Segment",
        comodel_name="mailchimp.list.segment",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
    )
    mailchimp_create_date = fields.Datetime(
        string='Create Date',
        default=datetime.utcnow(),
        readonly=True
    )
    state = fields.Selection(
        string="Status",
        selection="state_selection",
        default='save',
    )
    parent_id = fields.Many2one(
        string='Parent Campaign',
        comodel_name='mailchimp.campaign',
        ondelete='cascade'
    )
    child_ids = fields.One2many(
        string='Child Campaigns',
        comodel_name='mailchimp.campaign',
        inverse_name='parent_id'
    )
    report_ids = fields.One2many(
        string="Reports",
        comodel_name="mailchimp.list.member.stats",
        inverse_name="campaign_id",
        readonly=True,
    )
    list_count = fields.Integer(
        string='Total Audience',
        related='list_id.list_count',
        readonly=1
    )
    segment_count = fields.Integer(
        string='Total Audience',
        related='segment_id.segment_count',
        readonly=1

    )
    # COUNTS
    sent_count = fields.Integer(
        string='Sent',
        readonly=1
    )
    bounce_count = fields.Integer(
        string='Bounce Count',
        readonly=1
    )
    receive_count = fields.Integer(
        string='Receive Count',
        compute='compute_receive_count',
        store=True
    )
    open_count = fields.Integer(
        string='Open Count',
        readonly=1
    )
    click_count = fields.Integer(
        string='Click Count',
        readonly=1
    )
    unsubscribe_count = fields.Integer(
        string='Unsubscribe Count',
        readonly=1
    )
    # RATES
    receive_rate = fields.Float(
        string='Receive Rate',
        compute='compute_rate',
        store=True
    )
    open_rate = fields.Float(
        string='Open Rate',
        compute='compute_rate',
        store=True
    )
    click_rate = fields.Float(
        string='Click Rate',
        compute='compute_rate',
        store=True
    )
    unsubscribe_rate = fields.Float(
        string='Unsubscribe Rate',
        compute='compute_rate',
        store=True
    )
    # STRING: COUNT (RATE)
    receive_str = fields.Char(
        string='Received',
        compute='compute_str',
        store=True
    )
    open_str = fields.Char(
        string='Opened',
        compute='compute_str',
        store=True
    )
    click_str = fields.Char(
        string='Clicked',
        compute='compute_str',
        store=True
    )
    unsubscribe_str = fields.Char(
        string='Unsubscribed',
        compute='compute_str',
        store=True
    )

    @api.model
    def state_selection(self):
        return [
            ('save', 'Draft'),
            ('sent', 'Sent'),
            ('other', 'Other')
        ]

    @api.onchange('list_id')
    def onchange_list_id(self):
        if self.list_id:
            self.segment_id = False
            self.from_name = self.list_id.from_name
            self.subject_line = self.list_id.subject

    @api.model
    def create(self, values):
        record = super(MailchimpCampaign, self).create(values)
        client = self.env['mailchimp.client'].get_client()
        if 'mailchimp_ref' not in values:
            mailchimp_ref = record._create_campaign(client)
            record.write({'mailchimp_ref': mailchimp_ref})
        return record

    def _create_campaign(self, client):
        data = {
            "recipients":
                {
                    "list_id": self.list_id.mailchimp_ref,
                    "segment_opts": {
                        "saved_segment_id": self.segment_id.mailchimp_ref,
                    }
                },
            "settings": self._get_settings(),
            "type": self.type,
        }
        return client.campaigns.create(data).get('id')

    def _get_settings(self):
        return {
            "title": self.name,
            "subject_line": self.subject_line,
            "from_name": self.from_name,
            "reply_to": self.reply_to,
        }

    @api.multi
    def write(self, values):
        self.ensure_one()
        record = super(MailchimpCampaign, self).write(values)
        client = self.env['mailchimp.client'].get_client()
        if any(key in values for key in
               ['name', 'subject_line', 'from_name', 'reply_to']):
            self._update_content(client)
        if 'list_id' in values:
            self._update_list(client)
        if 'segment_id' in values:
            self._update_segment(client)
        return record

    def _update_content(self, client):
        data = {
            "settings": self._get_settings()
        }
        return client.campaigns.update(self.mailchimp_ref, data)

    def _update_list(self, client):
        data = {
            "recipients":
                {
                    "list_id": self.list_id.mailchimp_ref,
                },
            "settings": self._get_settings(),
        }
        return client.campaigns.update(self.mailchimp_ref, data)

    def _update_segment(self, client):
        data = {
            "recipients":
                {
                    "segment_opts": {
                        "saved_segment_id": self.segment_id.mailchimp_ref,
                    }
                },
            "settings": self._get_settings(),
        }
        return client.campaigns.update(self.mailchimp_ref, data)

    @api.depends('sent_count', 'bounce_count')
    def compute_receive_count(self):
        for rec in self:
            rec.update({
                'receive_count': rec.sent_count - rec.bounce_count
            })

    @api.depends('receive_count', 'click_count', 'sent_count', 'open_count')
    def compute_rate(self):
        for rec in self:
            if not rec.sent_count:
                return True
            rec.update({
                'receive_rate': float(rec.receive_count) / rec.sent_count,

            })
            if not rec.receive_count:
                return True
            rec.update({
                'click_rate': float(rec.click_count) / rec.receive_count,
                'open_rate': float(rec.open_count) / rec.receive_count,
                'unsubscribe_rate': float(
                    rec.unsubscribe_count) / rec.receive_count,

            })

    @api.depends('click_count', 'click_rate', 'receive_count', 'receive_rate',
                 'open_count', 'open_rate', 'unsubscribe_count',
                 'unsubscribe_rate')
    def compute_str(self):
        for rec in self:
            rec.update({
                'click_str': self.reformat_str(rec.click_count,
                                               rec.click_rate),
                'receive_str': self.reformat_str(rec.receive_count,
                                                 rec.receive_rate),
                'open_str': self.reformat_str(rec.open_count,
                                              rec.open_rate),
                'unsubscribe_str': self.reformat_str(rec.unsubscribe_count,
                                                     rec.unsubscribe_rate),

            })

    def reformat_str(self, count, rate):
        return "%s (%.2f%%)" % (count, rate * 100)

    def action_view_leads(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        if self.segment_id.id:
            action['domain'] = [('segment_ids.id', '=', self.segment_id.id)]
            return action
        action['domain'] = [('list_ids.id', '=', self.list_id.id)]
        return action

    def action_view_stats(self):
        self.ensure_one()
        action = self.env.ref(
            'bso_mailchimp.crm_mailchimp_mailing_member_stats_action_specific'
        ).read()[0]
        action['domain'] = [('id', 'in', self.report_ids.ids)]
        return action

    @api.multi
    def action_fetch(self):
        """ create or update mailing.stats for each lead in
        mailing list of current campaign and childs
        based on mailing state """
        self.ensure_one()
        client = self.env['mailchimp.client'].get_client()
        self._fetch(client)

    def _fetch(self, client):
        for campaign_id in self.child_ids:
            campaign_id._fetch(client)
        self._update_stats(client)

    def _update_stats(self, client):
        if not self.is_campaign_sent(client):
            return False
        self._update_counts(client)
        self._update_members_stats(client)

    @api.model
    def is_campaign_sent(self, client):
        if self.state == 'sent':
            return True
        if self.state in ('save', 'other'):
            campaign = client.campaigns.get(
                campaign_id=self.mailchimp_ref)
            if campaign.get('status') == 'sent':
                self.update({'state': 'sent'})
                return True
        return False

    def _update_counts(self, client):
        report = client.reports.get(
            campaign_id=self.mailchimp_ref)
        open_count = report.get('opens', {}).get('unique_opens')
        sent_count = report.get('emails_sent')
        bounces = report.get('bounces', {})
        soft_bounces = bounces.get('soft_bounces')
        hard_bounces = bounces.get('hard_bounces')
        bounce_count = hard_bounces + soft_bounces
        click_count = report.get('clicks', {}).get('unique_clicks')
        unsubscribe_count = report.get('unsubscribed')
        return self.update({'open_count': open_count,
                            'sent_count': sent_count,
                            'bounce_count': bounce_count,
                            'click_count': click_count,
                            'unsubscribe_count': unsubscribe_count
                            })

    def _update_members_stats(self, client):
        if not self._get_leads():
            return True
        lead_emails = {l.email_from: l.id for l in self._get_leads()}
        for lead_activity in self._get_members_email_activity(client):
            lead_email = lead_activity.get('email_address', '').strip().lower()
            lead_id = lead_emails.get(lead_email)
            if not lead_id:
                continue
            activity = lead_activity.get('activity', {})
            if not activity:
                continue
            member_stats_values = {
                'sent': self._get_action_date(activity, 'sent'),
                'opened': self._get_action_date(activity, 'open'),
                'bounced': self._get_action_date(activity, 'bounce'),
                'clicked': self._get_action_date(activity, 'click'),
                'unsubscribed': self._get_action_date(activity, 'unsub'),
            }
            member_stats_id = self._get_member_stats_id(lead_id)
            if not member_stats_id:
                member_stats_values.update({
                    'campaign_id': self.id,
                    'lead_id': lead_id
                })
                self.env['mailchimp.list.member.stats'].create(
                    member_stats_values)
                continue
            member_stats_id.write(member_stats_values)

    def _get_members_email_activity(self, client):
        members_email_activity = client.reports.email_activity.all(
            self.mailchimp_ref,
            get_all=True).get('emails', [])
        return members_email_activity

    def _get_leads(self):
        if self.segment_id:
            return self.segment_id.lead_ids
        return self.list_id.lead_ids

    def _get_action_date(self, activity, action):
        if activity:
            for action_dict in activity:
                if action_dict.get('action') == action:
                    timestamp = action_dict.get('timestamp')
                    if timestamp:
                        return dateutil.parser.parse(timestamp)
        return False

    def _get_member_stats_id(self, lead_id):
        """ get a lead stats record """
        member_stats = self.report_ids.filtered(
            lambda r: r.lead_id.id == lead_id)
        return member_stats
