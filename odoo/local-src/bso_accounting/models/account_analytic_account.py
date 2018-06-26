# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    old_ref = fields.Char(string="Old ref")
