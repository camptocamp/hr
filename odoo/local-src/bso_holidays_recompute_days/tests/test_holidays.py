# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHolidays(TransactionCase):

    def setUp(self):
        super(TestHolidays, self).setUp()
        self.company = self._get_fr_company()
        self.status = self._get_status()
        self.company.legal_holidays_status_id = self.status.id
        self.employee = self._get_fr_employee()
        self._check_or_create_fr_public_holiday_line()
        self.holidays_obj = self.env['hr.holidays']

    def _get_fr_company(self):
        return self.env['res.company'].create({
            'name': 'FR company',
            'country_id': self.env.ref('base.fr').id,
        })

    def _get_status(self):
        return self.env['hr.holidays.status'].create({
            'name': 'FR Travail à distance',
            'exclude_public_holidays': True,
            'exclude_rest_days': True,
            'limit': True,
            'company_id': self.company.id
        })

    def _get_fr_employee(self):
        partner = self.env['res.partner'].create({
            'name': 'Test user',
            'country_id': self.env.ref('base.fr').id
        })
        return self.env['hr.employee'].create({
            'name': 'Test Employee',
            'company_id': self.company.id,
            'address_id': partner.id
        })

    def _check_or_create_fr_public_holiday_line(self):
        fr_public_holidays_2019 = self.env['hr.holidays.public'].search([
            ('year', '=', 2019),
            ('country_id', '=', self.env.ref('base.fr').id)
        ])
        lundi_de_pentecote = self.env['hr.holidays.public.line'].search([
            ('name', '=', 'Lundi de Pentecôte'),
            ('date', '=', '2019-06-10'),
            ('year_id', '=', fr_public_holidays_2019.id)
        ])
        if not lundi_de_pentecote:
            return fr_public_holidays_2019.write({
                "line_ids": [(0, 0, {
                    'name': 'Lundi de Pentecôte',
                    'date': '2019-06-10', })]
            })
        return

    def test_holidays_case1(self):
        date_from = '2019-06-04 08:00:00'
        date_to = '2019-06-04 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -1)

    def test_holidays_case2(self):
        date_from = '2019-06-04 08:00:00'
        date_to = '2019-06-04 13:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -0.5)

    def test_holidays_case3(self):
        date_from = '2019-06-04 14:00:00'
        date_to = '2019-06-04 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -0.5)

    def test_holidays_case4(self):
        date_from = '2019-06-04 08:00:00'
        date_to = '2019-06-06 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -3)

    def test_holidays_case5(self):
        date_from = '2019-06-04 14:00:00'
        date_to = '2019-06-06 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -2.5)

    def test_holidays_case6(self):
        date_from = '2019-06-04 08:00:00'
        date_to = '2019-06-06 13:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -2.5)

    def test_holidays_case7(self):
        date_from = '2019-06-10 08:00:00'
        date_to = '2019-06-10 18:00:00'
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Travail à distance',
                'holiday_status_id': self.status.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': self.employee.id,
                'type': 'remove',
            })

    def test_holidays_case8(self):
        date_from = '2019-06-10 08:00:00'
        date_to = '2019-06-10 13:00:00'
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Travail à distance',
                'holiday_status_id': self.status.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': self.employee.id,
                'type': 'remove',
            })

    def test_holidays_case9(self):
        date_from = '2019-06-10 14:00:00'
        date_to = '2019-06-10 18:00:00'
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Travail à distance',
                'holiday_status_id': self.status.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': self.employee.id,
                'type': 'remove',
            })

    def test_holidays_case10(self):
        date_from = '2019-06-07 08:00:00'
        date_to = '2019-06-11 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -2)

    def test_holidays_case11(self):
        date_from = '2019-06-08 14:00:00'
        date_to = '2019-06-11 18:00:00'

        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee.id,
            'type': 'remove',
        })
        self.assertEqual(holiday.number_of_days, -1)

    def test_holidays_case12(self):
        date_from = '2019-06-08 14:00:00'
        date_to = '2019-06-09 18:00:00'
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Travail à distance',
                'holiday_status_id': self.status.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': self.employee.id,
                'type': 'remove',
            })

    def test_holidays_allocation_0_days(self):
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Travail à distance',
                'holiday_status_id': self.status.id,
                'employee_id': self.employee.id,
                'type': 'add',
                'number_of_days_temp': 0
            })

    def test_holidays_allocation_10_days(self):
        holiday = self.holidays_obj.create({
            'name': 'Travail à distance',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee.id,
            'type': 'add',
            'number_of_days_temp': 10
        })
        self.assertEqual(holiday.number_of_days, 10)

    def test_create_holiday_without_leave_balance(self):
        self.employee.write({'remaining_leaves': 0})
        status_id = self.env.ref('hr_holidays.holiday_status_cl')
        date_from = '2019-06-08 14:00:00'
        date_to = '2019-06-11 18:00:00'
        with self.assertRaises(ValidationError):
            self.holidays_obj.create({
                'name': 'Sick leave',
                'holiday_status_id': status_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'employee_id': self.employee.id,
                'type': 'remove',
            })
