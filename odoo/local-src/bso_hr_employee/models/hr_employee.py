# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_contractor = fields.Boolean(
        string='Is Contractor',
        default=False
    )
    entry_date = fields.Date(
        string='Entry Date',
        required=True,
        default=fields.Date.today,
    )
