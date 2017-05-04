# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    project_zone_id = fields.Many2one(comodel_name='project.zone',
                                      string='Project Zone')
    project_process_id = fields.Many2one(comodel_name='project.process',
                                         string='Project Process')
    project_market_id = fields.Many2one(comodel_name='project.market',
                                        string='Project Market')
