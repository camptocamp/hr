from collections import namedtuple

from odoo import models, fields, api, exceptions


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.constrains('date_from', 'date_to', 'holiday_status_id', 'type')
    def _check_overlap(self):
        if not self.holiday_status_id.limit:
            if not (
                    self.holiday_status_id.start_date and
                    self.holiday_status_id.end_date
            ) or self.type == 'add':
                return True

            Range = namedtuple('Range', ['start', 'end'])

            start_date = HrHolidays.str_to_date(
                self.holiday_status_id.start_date)

            end_date = HrHolidays.str_to_date(
                self.holiday_status_id.end_date)

            date_from = HrHolidays.str_to_date(self.date_from)

            date_to = HrHolidays.str_to_date(self.date_to)

            leave_type = Range(start=start_date, end=end_date)
            current_leave = Range(start=date_from, end=date_to)

            if not (
                    current_leave.start <= leave_type.end and
                    current_leave.end >= leave_type.start
            ):
                raise exceptions.ValidationError(
                    'Your leave must have at least one day in the '
                    'authorized selected "Leave type" period'
                )

        return True

    @staticmethod
    def str_to_date(str_date):
        return fields.Date.from_string(str_date)
