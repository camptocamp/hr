from odoo import models, fields, api, exceptions
from collections import namedtuple


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.constrains('date_from', 'date_to', 'holiday_status_id')
    def _check_overlap(self):
        if not self.holiday_status_id.limit:
            if (
                    self.holiday_status_id.start_date is False or
                    self.holiday_status_id.end_date is False
            ):
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

            latest_start = max(current_leave.start, leave_type.start)
            earliest_end = min(current_leave.end, leave_type.end)

            overlap = max(0, (earliest_end - latest_start).days + 1)
            if overlap == 0:
                raise exceptions.ValidationError(
                    'Your leave must have at least one day in the '
                    'authorized selected "Leave type" period'
                )
        return True

    @staticmethod
    def str_to_date(str_date):
        return fields.Date.from_string(str_date)

