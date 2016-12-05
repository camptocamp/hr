# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('seniority_days',
                 'partial_time', 'partial_percent',
                 'company_id.legal_holidays_status_id',
                 'company_id.legal_holidays_status_id.annual_leaves'
                 )
    def _get_per_month_legal_allocation(self):
        for rec in self:
            legal = rec.company_id.legal_holidays_status_id.annual_leaves
            days = (legal + rec.seniority_days) / 12.
            if rec.partial_time:
                days *= rec.partial_percent / 100.
            rec.per_month_legal_allocation = days

    def _get_per_month_rtt(self):
        for rec in self:
            rtt = self.env['hr.holidays.status'].search(
                [('is_rtt', '=', True)]
            ).annual_leaves
            rec.per_month_rtt_allocation = rtt / 12.0

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
    partial_time = fields.Boolean(default=False)
    partial_percent = fields.Integer()
    per_month_rtt_allocation = fields.Float(
        digits=(16, 3),
        compute='_get_per_month_rtt'
    )


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    name = fields.Char(required=True)
