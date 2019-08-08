# -*- coding:utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, api, fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class HrHolidays(models.Model):
    _inherit = "hr.holidays"
    number_of_days_temp = fields.Float(
        inverse='_set_number_of_days_temp',
        compute='_compute_number_of_days_temp',
        store=True,
    )

    @api.constrains('number_of_days_temp')
    def _check_number_of_days_temp(self):
        for record in self:
            if not record.number_of_days_temp:
                raise ValidationError(
                    "The number of days must be greater than 0.")

    @api.multi
    @api.depends('holiday_status_id', 'employee_id', 'date_from', 'date_to')
    def _compute_number_of_days_temp(self):
        for holiday in self:
            if holiday.type == 'add':
                continue
            date_from = holiday.date_from
            date_to = holiday.date_to
            if (date_to and date_from) and (date_from <= date_to):
                number_of_days_temp = holiday._recompute_number_of_days()
            else:
                number_of_days_temp = 0
            holiday.update({'number_of_days_temp': number_of_days_temp})

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        return

    @api.onchange('employee_id')
    def _onchange_employee(self):
        return

    @api.onchange('date_from')
    def _onchange_date_from(self):
        return

    @api.onchange('date_to')
    def _onchange_date_to(self):
        return

    def _recompute_number_of_days(self):
        number_of_days = 0
        date_from = self.date_from
        date_to = self.date_to

        if not date_from or not date_to:
            return 0

        status_id = self.holiday_status_id.id or self.env.context.get(
            'holiday_status_id',
            False)
        employee_id = self.employee_id.id
        if employee_id and date_from and date_to and status_id:
            employee = self.env['hr.employee'].browse(employee_id)
            status = self.env['hr.holidays.status'].browse(status_id)
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            date_dt = date_from
            while date_dt <= date_to:
                day = .5 if self.is_half_day(date_dt) else 1
                if not employee.work_scheduled_on_day(
                        date_dt,
                        status.exclude_public_holidays,
                        status.exclude_rest_days):
                    day *= 0
                number_of_days += day
                date_dt += relativedelta(days=1)
        return number_of_days

    def is_half_day(self, date_dt):
        date_from_dt = fields.Date.from_string(self.date_from)
        date_to_dt = fields.Date.from_string(self.date_to)

        if date_dt == date_from_dt == date_to_dt:
            return self.leave_starts_after_13_30() or \
                   self.leave_ends_before_13_30()

        if date_dt == date_from_dt:
            return self.leave_starts_after_13_30()

        if date_dt == date_to_dt:
            return self.leave_ends_before_13_30()

        return False

    def leave_starts_after_13_30(self):
        from_dt = datetime.datetime.strptime(self.date_from, DATETIME_FORMAT)
        from_dt_h = fields.Datetime.context_timestamp(self, from_dt)
        from_dt_h1330 = fields.Datetime.context_timestamp(
            self, from_dt).replace(hour=13, minute=30)
        if from_dt_h > from_dt_h1330:
            return True
        return False

    def leave_ends_before_13_30(self):
        to_dt = datetime.datetime.strptime(self.date_to, DATETIME_FORMAT)
        to_dt_h = fields.Datetime.context_timestamp(self, to_dt)
        to_dt_h1330 = fields.Datetime.context_timestamp(
            self, to_dt).replace(hour=13, minute=30)
        if to_dt_h < to_dt_h1330:
            return True
        return False

    def _set_number_of_days_temp(self):
        for holiday in self:
            pass
