# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def get_default_network_api(self):
        api = self.env['bso.network.api'].search([], limit=1)
        return api

    network_api_id = fields.Many2one(comodel_name='bso.network.api',
                                     string="Network API",
                                     default=get_default_network_api)
