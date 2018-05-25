# -*- coding: utf-8 -*-
import calendar
import logging
from datetime import datetime, date, time

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from pytz import timezone

_logger = logging.getLogger(__name__)


class HrHolidaysReport(models.Model):
    _name = "hr.holidays.report"
    _description = "Leave report"
    _order = 'id DESC'

    _sql_constraints = [
        ('name_unique', 'UNIQUE (name)', 'Report already exists')
    ]

    name = fields.Char(
        string='Report',
        compute='compute_name',
        store=True
    )
    start_date = fields.Datetime(
        string='Start Date',
        default=lambda self: self._get_start_date(),
        readonly=True
    )
    end_date = fields.Datetime(
        string='End Date',
        default=lambda self: self._get_end_date(),
        readonly=True
    )
    last_report_date = fields.Datetime(
        string='Last Report Date',
        default=lambda self: self._get_last_report_date(),
        readonly=True
    )
    report_lines = fields.One2many(
        string='Report Lines',
        comodel_name='hr.holidays.report.line',
        inverse_name='holiday_report_id',
        compute='compute_report_lines',
        store=True
    )

    # DEFAULTS

    @api.model
    def _get_start_date(self):
        return datetime.combine(date.today(), time()).replace(day=1)

    @api.model
    def _get_end_date(self):
        return self._get_start_date() + relativedelta(months=1, seconds=-1)

    @api.model
    def _get_last_report_date(self):
        last_report = self.env[self._name].search([], limit=1, order='id desc')
        return last_report.create_date

    # COMPUTES

    @api.depends('start_date')
    def compute_name(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.start_date)
            month_str = calendar.month_name[start_date.month]
            rec.update({
                'name': "Report %s %s" % (month_str, start_date.year)
            })

    @api.depends('start_date', 'end_date')
    def compute_report_lines(self):
        for rec in self:
            lines = []

            start_date = rec.start_date
            end_date = rec.end_date
            last_report_date = rec.last_report_date

            validated = self._get_holidays_validated(start_date, end_date)
            for leave in validated:
                item = self._get_line_item(leave, start_date, end_date)
                lines.append((0, 0, item))

            missing = self._get_holidays_missing(last_report_date, start_date)
            for leave in missing:
                item = self._get_line_item(leave, last_report_date, start_date)
                lines.append((0, 0, item))

            refused = self._get_holidays_refused(last_report_date, start_date)
            for leave in refused:
                item = self._get_line_item(leave, last_report_date, start_date)
                lines.append((0, 0, item))

            rec.update({
                'report_lines': lines
            })

    # TOOLS

    @api.model
    def _get_holidays_validated(self, start_date, end_date):
        # browse validated holidays for given period
        return self.env['hr.holidays'].search([
            ('state', 'in', ['validate']),
            ('type', 'in', ['remove']),
            ('date_to', '>', start_date),
            ('date_from', '<', end_date)
        ])

    @api.model
    def _get_holidays_missing(self, last_report_date, start_date):
        # browse missing holidays from previous report
        if not last_report_date:
            return []
        return self.env['hr.holidays'].search([
            ('state', 'in', ['validate']),
            ('type', 'in', ['remove']),
            ('date_validated', '>', last_report_date),
            ('date_to', '>', last_report_date),
            ('date_from', '<', start_date)
        ])

    @api.model
    def _get_holidays_refused(self, last_report_date, start_date):
        # browse refused holidays from previous report
        if not last_report_date:
            return []
        return self.env['hr.holidays'].search([
            ('state', 'in', ['refuse']),
            ('type', 'in', ['remove']),
            ('date_validated', '<', last_report_date),
            ('date_refused', '>', last_report_date),
            ('date_to', '<', start_date)
        ])

    @api.model
    def _get_line_item(self, holiday_id, start_date, end_date):
        # Build line item with static content
        employee_id = holiday_id.employee_id
        holiday_status_id = holiday_id.holiday_status_id
        return {
            'holiday_id': holiday_id.id,
            'employee_id': employee_id.id,
            'company_id': employee_id.company_id.id,
            'holiday_status_id': holiday_status_id.id,
            'holiday_state': holiday_id.state,
            'start_date': max(holiday_id.date_from, start_date),
            'end_date': min(holiday_id.date_to, end_date),
            'days': self._get_line_item_days(holiday_id, start_date, end_date)
        }

    @api.model
    def _get_line_item_days(self, holiday_id, start_date, end_date):
        if self._is_same_month(holiday_id):
            days = - holiday_id.number_of_days  # As positive value
        else:
            days = self._get_days_in_period(holiday_id, start_date, end_date)
        if holiday_id.state == 'refuse':
            days = - days
        return days

    @api.model
    def _is_same_month(self, holiday_id):
        dt_from = fields.Datetime.from_string(holiday_id.date_from)
        dt_to = fields.Datetime.from_string(holiday_id.date_to)
        return dt_from.month == dt_to.month

    @api.model
    def _get_days_in_period(self, holiday_id, start_date, end_date):
        date_from, date_to = self._to_user_tz_naive(holiday_id)
        lower_date = self._get_lower_date(date_from, start_date, holiday_id)
        upper_date = self._get_upper_date(date_to, end_date, holiday_id)
        return self._get_days(lower_date, upper_date, holiday_id)

    @api.model
    def _to_user_tz_naive(self, holiday_id):
        dt_from = fields.Datetime.from_string(holiday_id.date_from)
        dt_to = fields.Datetime.from_string(holiday_id.date_to)
        u_tz = holiday_id.employee_id.user_id.tz or 'UTC'
        return self._to_tz_naive(dt_from, u_tz), self._to_tz_naive(dt_to, u_tz)

    @api.model
    def _to_tz_naive(self, dt, tz):
        dt_tz = timezone('UTC').localize(dt).astimezone(timezone(tz))
        return str(dt_tz.replace(tzinfo=None))

    @api.model
    def _get_lower_date(self, date_from, start_date, holiday_id):
        lower_date = max(date_from, start_date)
        lower_date = self._get_nearest_workday(lower_date, holiday_id, step=1)
        return lower_date

    @api.model
    def _get_upper_date(self, date_to, end_date, holiday_id):
        upper_date = min(date_to, end_date)
        upper_date = self._get_nearest_workday(upper_date, holiday_id, step=-1)
        return upper_date

    @api.model
    def _get_nearest_workday(self, date_str, holiday_id, step):
        dt = fields.Datetime.from_string(date_str)
        while not self._is_work_day(dt, holiday_id):
            dt += relativedelta(days=step)
        return str(dt)

    @api.model
    def _is_work_day(self, date_dt, holiday_id):
        employee = holiday_id.employee_id
        status = holiday_id.holiday_status_id
        return employee.work_scheduled_on_day(
            date_dt,
            status.exclude_public_holidays,
            status.exclude_rest_days)

    @api.model
    def _get_days(self, start_date, end_date, holiday_id):
        holiday = self.env['hr.holidays'].with_context(tz='UTC').new({
            'date_from': start_date,
            'date_to': end_date,
            'type': holiday_id.type,
            'holiday_status_id': holiday_id.holiday_status_id.id,
            'employee_id': holiday_id.employee_id.id,
        })
        holiday._onchange_date_from()
        return - holiday.number_of_days  # As positive value

    # ACTIONS

    @api.multi
    def open_report_lines(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "hr.holidays.report.line",
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [('holiday_report_id', '=', self.id)],
            "context": {'search_default_group_employee_leave_type': 1},
        }
