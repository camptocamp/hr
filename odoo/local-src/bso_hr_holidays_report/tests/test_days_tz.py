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
            # Overlap on previous month
            # Should begin at 2018-05-02 00:00:00 as 01 is day off in FR
            ('2018-04-23 14:00:00', '2018-05-03 13:00:00', 1.5),
            ('2018-04-23 09:00:00', '2018-05-03 19:00:00', 2),
            # Same month
            ('2018-05-22 14:00:00', '2018-05-25 13:00:00', 3),
            ('2018-05-22 14:00:00', '2018-05-25 19:00:00', 3.5),
            ('2018-05-22 09:00:00', '2018-05-25 13:00:00', 3.5),
            ('2018-05-22 09:00:00', '2018-05-25 19:00:00', 4),
            # Overlap on next month
            # Should stop at 2018-05-31 23:59:59
            ('2018-05-24 14:00:00', '2018-06-04 13:00:00', 5.5),
            ('2018-05-24 09:00:00', '2018-06-04 19:00:00', 6),
        ]
        holidays = []
        idx = 0
        for start_date, end_date, expected_days in scenarios:
            name = 'user_%s' % idx
            employee = self._create_employee(name, tz)
            holiday = self._create_holiday(employee, start_date, end_date)
            holidays.append((holiday, expected_days))
            idx += 1

        self.env['hr.holidays.report'].create({
            'year': 2018,
            'month': 5,
            'last_create': False
        })

        for holiday, expected_days in holidays:
            reported_days = self._get_reported_days(holiday)
            self.assertEqual(expected_days, reported_days)

    def _create_employee(self, name, tz):
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
            'user_id': user_id.id,
            'address_id': self._get_company().partner_id.id,
        })
        return employee_id

    def _get_company(self, name='BSO Network Solutions SAS'):
        return self.env['res.company'].search([('name', '=', name)])[0]

    def _create_holiday(self, employee_id, start_date, end_date):
        holiday_id = self.env['hr.holidays'].create({
            'type': 'remove',
            'employee_id': employee_id.id,
            'holiday_status_id': self._get_holiday_status().id,
            'date_from': self._to_utc_naive(start_date, employee_id),
            'date_to': self._to_utc_naive(end_date, employee_id)
        })
        holiday_id._onchange_date_from()
        holiday_id.action_validate()
        return holiday_id

    def _get_holiday_status(self, name='FR Travail à distance'):
        return self.env['hr.holidays.status'].search([('name', '=', name)])[0]

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
