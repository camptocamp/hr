# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Employee(models.Model):
    _inherit = 'hr.employee'

    passport_expiration = fields.Date(
        string='Passport Expiration'
    )
    mobile_extension = fields.Char(
        string='Mobile Extension',
    )
    last_yearly_meeting = fields.Date(
        string='Last Yearly Meeting'
    )
    last_professional_assessment = fields.Date(
        string='Last Professional Assessment'
    )
    employee_status_id = fields.Many2one(
        'hr.employee.status',
        string='Employee Status',
        related="contract_id.employee_status_id",
        readonly=True,
    )
    coefficient = fields.Integer(
        'Coefficient',
        related="contract_id.coefficient",
        readonly=True,
    )
    classification = fields.Char(
        string='Classification',
        related="contract_id.classification",
        readonly=True,
    )


class EmployeeStatus(models.Model):
    _name = 'hr.employee.status'

    name = fields.Char(
        string='Name',
    )
