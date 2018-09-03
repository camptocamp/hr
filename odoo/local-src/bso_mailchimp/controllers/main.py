# -*- coding: utf-8 -*-

import re

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

import odoo
from odoo import http


class WebhookController(http.Controller):
    @http.route(['/bso_mailchimp/webhooks'], type='http',
                auth='none', method=['POST'], csrf=False)
    def webhooks(self, **post):
        ensure_db()

        if post.get('type') in ['unsubscribe', 'subscribe']:
            self._webhook_lead(post)
        if post.get('type') == 'campaign':
            self._webhook_campaign(post)

    def _webhook_lead(self, post):
        request.uid = odoo.SUPERUSER_ID
        env = request.env

        mailchimp_list_ref = post.get('data[list_id]')
        mailchimp_list = env['mailchimp.list'].search([
            ('mailchimp_ref', '=', mailchimp_list_ref)
        ], limit=1)
        if not mailchimp_list:
            return

        email = post.get('data[email]')
        fname = post.get('data[merges][FNAME]')
        lname = post.get('data[merges][LNAME]')
        if not fname and not lname:
            email_split = email.split('@')[0]
            name = " ".join(re.findall("[a-zA-Z]+", email_split))
        else:
            name = "%s %s" % (fname, lname)
        email_formatted = env['mailchimp.client'].format_email(email)
        lead = env['crm.lead'].search([
            ('email_from', '=', email_formatted)
        ], limit=1)
        if not lead:
            lead = env['crm.lead'].create({'email_from': email_formatted,
                                           'name': name})

        if post.get('data[action]') == 'unsub':
            mailchimp_list.write({
                'mailchimp_ref': mailchimp_list_ref,  # !update MC
                'opt_out_lead_ids': [(4, lead.id)],  # Add
                'lead_ids': [(3, lead.id)]  # Remove
            })
            odoo_segments = env['mailchimp.list.segment'].search([
                ('list_id', '=', mailchimp_list.id),
                ('lead_ids', 'in', [lead.id])])
            for odoo_segment in odoo_segments:
                odoo_segment.write({
                    'mailchimp_ref': odoo_segment.mailchimp_ref,  # !update MC
                    'lead_ids': [(3, lead.id)],  # Remove
                })
        else:
            mailchimp_list.write({
                'mailchimp_ref': mailchimp_list_ref,  # !update MC
                'opt_out_lead_ids': [(3, lead.id)],  # Remove
                'lead_ids': [(4, lead.id)]  # Add
            })

    def _webhook_campaign(self, post):
        request.uid = odoo.SUPERUSER_ID
        env = request.env

        mailchimp_list_ref = post.get('data[list_id]')
        mailchimp_list = env['mailchimp.list'].search([
            ('mailchimp_ref', '=', mailchimp_list_ref)
        ], limit=1)
        if not mailchimp_list:
            return

        subject = post.get('data[subject]')
        mailchimp_campaign = env['mailchimp.campaign'].search([
            ('subject_line', '=', subject),
            ('list_id', '=', mailchimp_list.id)
        ])
        if not mailchimp_campaign or len(mailchimp_campaign) > 1:
            return

        mailchimp_campaign.write({
            'mailchimp_ref': mailchimp_campaign.mailchimp_ref,  # !update MC
            'state': 'sent'
        })
