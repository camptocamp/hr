# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import TransactionCase
from pytz import timezone


class TestDays(TransactionCase):
    def test_london(self):
        self._assert_days(tz='Europe/London')

    def test_paris(self):
        self._assert_days(tz='Europe/Paris')

    def test_new_york(self):
        self._assert_days(tz='America/New_York')

    def test_hong_kong(self):
        self._assert_days(tz='Asia/Hong_Kong')

    def _assert_days(self, tz):
        scenarios = [
            # Overlap on previous month (should begin at 2017-09-03 00:00:00)
            ('2017-08-30 14:00:00', '2017-09-04 13:00:00', 1.5),
            ('2017-08-30 09:00:00', '2017-09-04 19:00:00', 2),
            # Same month
            ('2017-09-18 14:00:00', '2017-09-21 13:00:00', 3),
            ('2017-09-18 14:00:00', '2017-09-21 19:00:00', 3.5),
            ('2017-09-18 09:00:00', '2017-09-21 13:00:00', 3.5),
            ('2017-09-18 09:00:00', '2017-09-21 19:00:00', 4),
            # Overlap on next month (should stop at 2017-09-29 23:59:59)
            ('2017-09-22 14:00:00', '2017-10-03 13:00:00', 5.5),
            ('2017-09-22 09:00:00', '2017-10-03 19:00:00', 6),
            # Over month
            ('2017-08-30 09:00:00', '2017-10-03 19:00:00', 21)
        ]
        created_holidays = []
        for start_date, end_date, expected_days in scenarios:
            holiday_id = self._create_holiday(start_date, end_date, tz)
            created_holidays.append((holiday_id, expected_days))

        self.env['hr.holidays.report'].create({
            'year': 2017,
            'month': 9,
            'last_create': False
        })

        for holiday_id, expected_days in created_holidays:
            reported_days = self._get_reported_days(holiday_id)
            self.assertEqual(expected_days, reported_days,
                             holiday_id.employee_id.name)

    def _create_holiday(self, start_date, end_date, tz):
        employee_id = self._create_employee(start_date, end_date, tz)
        holiday_status_id = self._create_holiday_status()
        holiday_id = self.env['hr.holidays'].create({
            'type': 'remove',
            'employee_id': employee_id.id,
            'holiday_status_id': holiday_status_id.id,
            'date_from': self._to_utc_naive(start_date, employee_id),
            'date_to': self._to_utc_naive(end_date, employee_id)
        })
        holiday_id._onchange_date_from()
        holiday_id.action_validate()
        return holiday_id

    def _create_employee(self, start_date, end_date, tz):
        name = "%s %s" % (start_date, end_date)
        user_id = self.env['res.users'].with_context({
            'tracking_disable': True,
            'no_reset_password': True,
            'mail_create_nosubscribe': True
        }).create({
            'name': name,
            'login': "%s@test.com" % name,
            'password': 'test',
            'partner_id': self.env.user.partner_id.id,
            'tz': tz
        })
        employee_id = self.env['hr.employee'].create({
            'name': name,
            'user_id': user_id.id
        })
        return employee_id

    def _create_holiday_status(self):
        return self.env['hr.holidays.status'].create({
            'name': 'Test Holiday',
            'exclude_rest_days': True,
            'limit': True
        })

    def _to_utc_naive(self, date_str, employee_id):
        """Odoo stores Datetime as UTC"""
        dt = fields.Datetime.from_string(date_str)
        user_tz = employee_id.user_id.tz
        dt_utc = timezone(user_tz).localize(dt).astimezone(timezone('UTC'))
        return str(dt_utc.replace(tzinfo=None))

    def _get_reported_days(self, holiday_id):
        return self.env['hr.holidays.report.line'].search([
            ('holiday_id', '=', holiday_id.id)
        ])[0].days
