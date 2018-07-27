# -*- coding: utf-8 -*-

from mailchimp3 import MailChimp
from odoo.exceptions import ValidationError

from odoo import models


class MailchimpClient(models.TransientModel):
    _name = "mailchimp.client"

    def get_client(self):
        conf = self.env['ir.config_parameter']
        API_USER = conf.get_param('mailchimp.api_user')
        API_KEY = conf.get_param('mailchimp.api_key')
        return MailChimp(mc_api=API_KEY, mc_user=API_USER)

    def format_email(self, email):
        return email.strip().lower()

    def get_lead_email(self, lead):
        if lead.email_from:
            return lead.email_from
        raise ValidationError(
            "You need to set email for %s" % lead.name)


def handle_segment_exceptions(f):
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception:
            segment = args[0]
            client = args[1]
            # Import List
            mailchimp_list = client.lists.get(segment.list_id.mailchimp_ref)
            segment.env['mailchimp.settings']._import_list(
                client,
                mailchimp_list)
            # Import Segment
            mailchimp_segment = client.lists.segments.get(
                segment.list_id.mailchimp_ref, segment.mailchimp_ref)
            segment.env['mailchimp.settings']._import_segment(
                client,
                mailchimp_segment,
                segment.list_id.mailchimp_ref)

    return wrapper


def handle_list_exceptions(f):
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception:
            odoo_list = args[0]
            client = args[1]
            mailchimp_list = client.lists.get(odoo_list.mailchimp_ref)
            odoo_list.env['mailchimp.settings']._import_list(client,
                                                             mailchimp_list)

    return wrapper
