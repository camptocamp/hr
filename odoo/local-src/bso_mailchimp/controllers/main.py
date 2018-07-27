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
            return
        if post.get('type') == 'campaign':
            self._webhook_campaign(post)
            return

    def _webhook_lead(self, post):
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        list_ref = post.get('data[list_id]')
        email = post.get('data[email]')
        odoo_list = env['mailchimp.list'].search([
            ('mailchimp_ref', '=', list_ref)
        ], limit=1)
        if not odoo_list:
            return
        email_formatted = env['mailchimp.client'].format_email(email)
        lead = env['crm.lead'].search([
            ('email_from', '=', email_formatted)], limit=1)
        if not lead:
            lead = env['crm.lead'].create({'email_from': email_formatted})
        if post.get('data[action]') == 'unsub':
            odoo_list.write(
                {'opt_out_lead_ids': [(4, lead.id)],
                 'lead_ids': [(3, lead.id)]})
            odoo_segments = env['mailchimp.segment'].search([
                ('list_id', '=', odoo_list.id), ('lead_ids', 'in', [lead.id])])
            if not odoo_segments:
                return
            odoo_segments.write({'lead_ids': [(3, lead.id)]})

        else:
            odoo_list.write(
                {'opt_out_lead_ids': [(3, lead.id)],
                 'lead_ids': [(4, lead.id)]})

        # settings._import_list(client, list_dict)
        # settings._import_list_segments(client, list_dict)

        # email = post.get('data[email]')
        # email_formatted = env['mailchimp.client'].format_email(email)
        # lead = env['crm.lead'].search([
        #     ('email_from', '=', email_formatted)
        # ], limit=1)
        # if not lead:
        #     lead = env['crm.lead'].create({'email_from': email_formatted})
        #
        # if post.get('data[action]') == 'unsub':
        #     action_lead_ids = 3  # delete
        #     action_opt_lead_ids = 4  # add
        # else:
        #     action_lead_ids = 4  # add
        #     action_opt_lead_ids = 3  # delete
        #
        # return mailchimp_list.sudo().write(
        #     {'opt_out_lead_ids': [(action_opt_lead_ids, lead.id)],
        #      'lead_ids': [(action_lead_ids, lead.id)]})

    def _webhook_campaign(self, post):
        request.uid = odoo.SUPERUSER_ID
        env = request.env
        subject = post.get('data[subject]')
        list_ref = post.get('data[list_id]')
        mailchimp_list = env['mailchimp.list'].search(
            [('mailchimp_ref', '=', list_ref)], limit=1)
        if not mailchimp_list:
            return
        mailchimp_campaign = self.search(
            [('subject_line', '=', subject),
             ('list_id', '=', mailchimp_list.id)])
        if not mailchimp_campaign or len(mailchimp_campaign) > 1:
            return
        mailchimp_campaign.write({'state': 'sent'})
