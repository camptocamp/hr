# -*- coding: utf-8 -*-

from odoo import api, models


class Lead(models.Model):
    _name = "crm.lead"
    _inherit = ['crm.lead', 'mail.thread']

    @api.multi
    def message_get_suggested_recipients(self):
        return []
