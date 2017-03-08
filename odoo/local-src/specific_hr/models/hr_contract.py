# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Contract(models.Model):
    _inherit = 'hr.contract'

    start_reason = fields.Char(
        string='Start Reason',
    )
    end_reason = fields.Char(
        string='End Reason',
    )
    activity_rate = fields.Float(
        'Activity Rate',
    )
    coefficient = fields.Integer(
        'Coefficient',
    )
    classification = fields.Char(
        string='Classification',
    )
    employee_status_id = fields.Many2one(
        'hr.employee.status',
        string='Employee Status',
        required=True,
    )
