# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('seniority_days')
    def _get_per_month_legal_allocation(self):
        for rec in self:
            legal = self.env['hr.holidays.status'].search(
                [('is_annual', '=', True),
                 ('company_id', '=', rec.company_id.id)],
                limit=1).annual_leaves
            rec.per_month_legal_allocation = (legal + rec.seniority_days) / 12.

    user_login = fields.Char()
    title = fields.Char(string="Employee Title")
    family_id = fields.Many2one(
        comodel_name='hr.employee.family',
        string="Family"
    )
    job_id = fields.Many2one(string="Job Profile")
    marital = fields.Selection(selection_add=[('pacs', 'PACS'),
                                              ('cohabiting', 'Cohabiting')])
    seniority_days = fields.Integer(default=0)
    per_month_legal_allocation = fields.Float(
        digits=(16, 3),
        compute='_get_per_month_legal_allocation'
    )


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    name = fields.Char(required=True)
