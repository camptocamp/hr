# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResUsers(models.Model):

    _inherit = 'res.users'

    external_number = fields.Char(
        copy=False,
        help="User's external phone number."
    )
