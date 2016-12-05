# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api, _


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    annual_leaves = fields.Float(
        'Annual leaves',
        digits=(16, 3),
    )

    @api.multi
    def update_leaves_allocation(self):
        for rec in self:
            emps = self.env['hr.employee'].search(
                [('company_id', '=', rec.company_id.id),
                 ('active', '=', True)])
            self.env['hr.holidays'].create_allocation(emps, rec)

    @api.model
    def update_leaves_cron(self):
        leaves = self.env['res.company'].search([]).mapped(
            'legal_holidays_status_id')
        leaves.update_leaves_allocation()


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    number_of_days_temp = fields.Float(digits=(16, 3))

    @api.model
    def create_allocation(self, employee_rs, leave_type):
        created = self.env['hr.holidays']
        for employee in employee_rs:
            vals = {
                'number_of_days_temp': employee.per_month_legal_allocation,
                'name': _('Auto Allocation'),
                'employee_id': employee.id,
                'type': 'add',
                'holiday_status_id': leave_type.id,
            }

            created |= self.create(vals)

        created.signal_workflow('validate')
