# -*- coding: utf-8 -*-

from odoo import api, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = ['res.partner', 'mail.thread']

    @api.multi
    def message_get_suggested_recipients(self):
        return []
