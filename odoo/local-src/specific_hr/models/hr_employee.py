# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    user_login = fields.Char()
    title = fields.Char(string="Employee Title")
    family_id = fields.Many2one(
        comodel_name='hr.employee.family',
        string="Family"
    )
    job_id = fields.Many2one(string="Job Profile")
    marital = fields.Selection(selection_add=[('pacs', 'PACS'),
                                              ('cohabiting', 'Cohabiting')])


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    name = fields.Char(required=True)
