# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    so_double_validation = fields.Selection(
        selection_add=[
            ('bso_three_step',
             'Get 3 levels of approvals to confirm a sale order (BSO)')]
    )
