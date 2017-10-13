# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_send_method = fields.Selection(
        selection=[
            ('snail_mail', 'Snail mail'),
            ('email', 'Email'),
            ('both', 'Both'),
        ],
        default='email',
    )
