# -*- coding: utf-8 -*-


import dateutil.parser

from odoo import fields, models, api


class MailchimpSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'mailchimp.settings'

    company = fields.Char(
        string="Company",
        required=True
    )
    address = fields.Char(
        string="Address",
        required=True
    )
    city = fields.Char(
        string="City",
        required=True
    )
    state = fields.Char(
        string="State",
        required=True
    )
    zip = fields.Char(
        string="Zip",
        required=True
    )
    country = fields.Char(
        string="Country",
        required=True
    )
    from_name = fields.Char(
        string="From Name",
        required=True
    )
    from_email = fields.Char(
        string="Form Email",
        required=True
    )
    subject = fields.Char(
        string="Subject",
    )
    language = fields.Char(
        string="Language",
        required=True
    )
    email_type_option = fields.Boolean(
        string="Email type option",
        required=True
    )
    reply_to = fields.Char(
        string="Reply to",
        required=True
    )
    type = fields.Selection(
        [
            ('regular', 'Regular'),
            ('plaintext', 'Plaintext'),
            ('absplit', 'Absplit'),
            ('rss', 'RSS'),
            ('variate ', 'Variate'),
        ],
        string="Type",
        required=True

    )
    permission_reminder = fields.Char(
        string="Permission reminder",
        required=True
    )
    api_key = fields.Char(
        string="API Key",
        required=True
    )
    api_user = fields.Char(
        string="API user",
        required=True
    )
    webhook_url = fields.Char(
        string="Webhook url",
    )

    @api.model
    def get_default_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'company': conf.get_param('mailchimp.company'),
            'address': conf.get_param('mailchimp.address'),
            'city': conf.get_param('mailchimp.city'),
            'state': conf.get_param('mailchimp.state'),
            'zip': conf.get_param('mailchimp.zip'),
            'country': conf.get_param('mailchimp.country'),
            'from_name': conf.get_param('mailchimp.from_name'),
            'from_email': conf.get_param('mailchimp.from_email'),
            'subject': conf.get_param('mailchimp.subject'),
            'language': conf.get_param('mailchimp.language'),
            'email_type_option': conf.get_param('mailchimp.email_type_option'),
            'reply_to': conf.get_param('mailchimp.reply_to'),
            'type': conf.get_param('mailchimp.type'),
            'permission_reminder': conf.get_param(
                'mailchimp.permission_reminder'),
            'api_key': conf.get_param('mailchimp.api_key'),
            'api_user': conf.get_param('mailchimp.api_user'),
            'webhook_url': conf.get_param('mailchimp.webhook_url'),
        }

    @api.one
    def set_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('mailchimp.company', self.company)
        conf.set_param('mailchimp.address', self.address)
        conf.set_param('mailchimp.city', self.city)
        conf.set_param('mailchimp.state', self.state)
        conf.set_param('mailchimp.zip', self.zip)
        conf.set_param('mailchimp.country', self.country)
        conf.set_param('mailchimp.from_name', self.from_name)
        conf.set_param('mailchimp.from_email', self.from_email)
        conf.set_param('mailchimp.subject', self.subject)
        conf.set_param('mailchimp.language', self.language)
        conf.set_param('mailchimp.email_type_option', self.email_type_option)
        conf.set_param('mailchimp.reply_to', self.reply_to)
        conf.set_param('mailchimp.type', self.type)
        conf.set_param('mailchimp.permission_reminder',
                       self.permission_reminder)
        conf.set_param('mailchimp.api_key', self.api_key)
        conf.set_param('mailchimp.api_user', self.api_user)
        conf.set_param('mailchimp.webhook_url', self.webhook_url)

    @api.multi
    def action_import_lists(self):
        self.ensure_one()
        client = self.env['mailchimp.client'].get_client()
        self._import_lists(client)

    @api.model
    def _import_lists(self, client):
        lists = client.lists.all(get_all=True).get('lists', [])
        for list_dict in lists:
            self._import_list(client, list_dict)

    def _import_list(self, client, list_dict):
        values = self._get_list_values(client, list_dict)
        mailchimp_list = self._get_model('mailchimp.list', list_dict.get('id'))
        if mailchimp_list:
            mailchimp_list.write(values)
        else:
            self.env['mailchimp.list'].create(values)
        self._cr.commit()

    def _get_list_values(self, client, list):
        settings = list.get('campaign_defaults', {})
        create_time = list.get('date_created')
        lead_ids, opt_out_lead_ids = self._get_list_leads(client, list)
        values = {'name': list.get('name'),
                  'mailchimp_ref': list.get('id'),
                  'lead_ids': [(6, 0, lead_ids)],
                  'opt_out_lead_ids': [(6, 0, opt_out_lead_ids)],
                  'from_name': settings.get('from_name'),
                  'from_email': settings.get('from_email'),
                  'subject': settings.get('subject'),
                  'language': settings.get('language'),
                  'permission_reminder': list.get('permission_reminder'),
                  'email_type_option': list.get('email_type_option'),
                  'mailchimp_create_date': dateutil.parser.parse(create_time)
                  }
        return values

    def _get_list_leads(self, client, list):
        members = client.lists.members.all(list_id=list.get('id'),
                                           get_all=True).get('members', [])
        return self._get_leads(members)

    def _get_leads(self, members):
        subscribed_members_emails = [m['email_address'].lower() for m in
                                     members
                                     if m.get('email_address')
                                     and m.get('status') == 'subscribed']
        unsubscribed_members_emails = [m['email_address'].lower() for m in
                                       members
                                       if m.get('email_address')
                                       and m.get('status') == 'unsubscribed']
        lead_ids = self.env['crm.lead'].search([
            ('email_from', 'in', subscribed_members_emails)
        ])
        opt_out_lead_ids = self.env['crm.lead'].search([
            ('email_from', 'in', unsubscribed_members_emails)
        ])
        return lead_ids.ids, opt_out_lead_ids.ids

    def _get_model(self, model_name, ref):
        mailchimp_model = self.env[model_name].search(
            [('mailchimp_ref', '=', ref)], limit=1)
        if not mailchimp_model:
            return False
        return mailchimp_model

    @api.multi
    def import_segments(self):
        self.ensure_one()
        client = self.env['mailchimp.client'].get_client()
        lists = client.lists.all(get_all=True).get('lists', [])
        for list_dict in lists:
            self._import_list_segments(client, list_dict)

    def _import_list_segments(self, client, list_dict):
        segments = client.lists.segments.all(
            list_id=list_dict.get('id'), get_all=True).get('segments', [])
        for segment_dict in segments:
            self._import_segment(client, segment_dict, list_dict.get('id'))

    def _import_segment(self, client, segment_dict, list_id):
        values = self._get_segment_values(client, list_id,
                                          segment_dict)
        mailchimp_segment = self._get_model('mailchimp.list.segment',
                                            segment_dict.get('id'))
        if mailchimp_segment:
            mailchimp_segment.write(values)
        else:
            self.env['mailchimp.list.segment'].create(values)
        self._cr.commit()

    def _get_segment_values(self, client, list_ref, segment):
        create_time = segment.get('created_at')
        lead_ids = self._get_segment_leads(client, list_ref, segment.get('id'))
        values = {'name': segment.get('name'),
                  'list_id': self._get_mailchimp_id(
                      'mailchimp.list', list_ref),
                  'mailchimp_ref': segment.get('id'),
                  'lead_ids': [(6, 0, lead_ids)],
                  'mailchimp_create_date': dateutil.parser.parse(create_time)}
        return values

    def _get_segment_leads(self, client, list_ref, segment_ref):
        members = client.lists.segments.members.all(
            list_ref, segment_ref, get_all=True).get('members', [])
        return self._get_leads(members)[0]

    def _get_mailchimp_id(self, model_name, list_ref):
        record = self.env[model_name].search([
            ('mailchimp_ref', '=', list_ref)
        ], limit=1)
        if record:
            return record.id

    @api.multi
    def import_campaigns(self):
        self.ensure_one()
        client = self.env['mailchimp.client'].get_client()
        campaigns = client.campaigns.all(get_all=True).get('campaigns', [])
        for campaign in campaigns:
            mailchimp_campaign = self._get_model('mailchimp.campaign',
                                                 campaign.get('id'))
            values = self._get_campaign_values(campaign)
            if not values.get('list_id'):
                continue
            if mailchimp_campaign:
                mailchimp_campaign.write(values)
            else:
                self.env['mailchimp.campaign'].create(values)
            self._cr.commit()

    def _get_campaign_values(self, campaign):
        settings = campaign.get('settings', {})
        create_time = campaign.get('create_time')
        values = {
            'name': settings.get('title'),
            'subject_line': settings.get('subject_line'),
            'list_id': self._get_mailchimp_id(
                'mailchimp.list',
                campaign.get('recipients', {}).get('list_id')),
            'segment_id': self._get_mailchimp_id(
                'mailchimp.list.segment',
                campaign.get('recipients').get('segment_opts', {}).get(
                    'saved_segment_id')),
            'mailchimp_ref': campaign.get('id'),
            'state': self._get_valid_state(campaign.get('status')),
            'from_name': settings.get('from_name'),
            'reply_to': settings.get('reply_to'),
            'type': campaign.get('type'),
            'mailchimp_create_date': dateutil.parser.parse(create_time)
        }
        return values

    def _get_valid_state(self, status):
        state_tuples = self.env['mailchimp.campaign'].state_selection()
        state_list = [state[0] for state in state_tuples]
        if status not in state_list:
            return 'other'
        return status

    @api.multi
    def fetch_all(self):
        client = self.env['mailchimp.client'].get_client()
        for campaign in self.env['mailchimp.campaign'].search([]):
            if not campaign.is_campaign_sent(client):
                continue
            campaign._update_counts(client)
