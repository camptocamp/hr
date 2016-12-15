# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from openerp import fields, models, api, _
from openerp import tools


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    annual_leaves = fields.Float(
        'Annual leaves',
        digits=(16, 3),
    )

    is_rtt = fields.Boolean('Is RTT')

    exclude_rest_days = fields.Boolean('Exclude week-end')

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
        self.search([('is_rtt', '=', True)]).update_leaves_allocation()


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    number_of_days_temp = fields.Float(digits=(16, 3))

    @api.model
    def create_allocation(self, employee_rs, leave_type):
        created = self.env['hr.holidays']
        for employee in employee_rs:
            if leave_type.is_annual:
                nb_days = employee.per_month_legal_allocation
            else:
                nb_days = employee.per_month_rtt_allocation
            vals = {
                'number_of_days_temp': nb_days,
                'name': _('Auto Allocation'),
                'employee_id': employee.id,
                'type': 'add',
                'holiday_status_id': leave_type.id,
            }

            created |= self.create(vals)

        created.signal_workflow('validate')

    def _compute_number_of_days(self, employee_id, date_to, date_from):
        diff_days = 0
        DATETIME_FORMAT = tools.DEFAULT_SERVER_DATETIME_FORMAT
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)

        from_dt_h = fields.Datetime.context_timestamp(self, from_dt)
        from_dt_h1330 = fields.Datetime.context_timestamp(
            self, from_dt).replace(hour=13, minute=30)

        to_dt_h = fields.Datetime.context_timestamp(self, to_dt)
        to_dt_h1330 = fields.Datetime.context_timestamp(
            self, to_dt).replace(hour=13, minute=30)
        if from_dt_h > from_dt_h1330:
            diff_days -= .5
        if to_dt_h < to_dt_h1330:
            diff_days += .5
        else:
            diff_days += 1

        date_from2 = fields.Datetime.from_string(date_from)
        date_to2 = fields.Datetime.from_string(date_to)

        date_from2 = date_from2.replace(hour=8, minute=0, second=0)
        date_to2 = date_to2.replace(hour=7, minute=59, second=59)

        days = super(HrHolidays, self)._compute_number_of_days(
            employee_id,
            date_to2.strftime(DATETIME_FORMAT),
            date_from2.strftime(DATETIME_FORMAT))

        return days + diff_days
