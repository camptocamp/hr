from odoo import exceptions
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestLeaveHolidayOverlap(common.TransactionCase):
    def setUp(self):
        super(TestLeaveHolidayOverlap, self).setUp()

        self.leave_status = self.env['hr.holidays.status'].create({
            'name': 'test holiday',
            'limit': False,
            'start_date': '2017-01-01',
            'end_date': '2017-01-31',
        })

        user = self.env['res.users'].create({
            'name': 'name test',
            'login': 'login',
            'email': 'test@bsonetwork.com'
        })
        self.employee = self.env['hr.employee'].create({
            'name': user.name,
            'user_id': user.id
        })

    def test_leave_creation_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env['hr.holidays'].create({
                'type': 'remove',
                'employee_id': self.employee.id,
                'holiday_status_id': self.leave_status.id,
                'holiday_type': 'employee',
                'date_from': '2017-02-05',
                'date_to': '2017-02-10'
            })

    def test_leave_creation_ok(self):
        leaves_before = self.env['hr.holidays'].search_count(
            [('employee_id', '=', self.employee.id)])
        self.env['hr.holidays'].create({
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_status.id,
            'type': 'remove',
            'holiday_type': 'employee',
            'date_from': '2017-01-05',
            'date_to': '2017-02-10'
        })
        leaves_after = self.env['hr.holidays'].search_count(
            [('employee_id', '=', self.employee.id)])
        self.assertEqual(leaves_after, leaves_before + 1)

    def test_allocation_creation_ok(self):
        leaves_before = self.env['hr.holidays'].search_count(
            [('employee_id', '=', self.employee.id)])
        self.env['hr.holidays'].create({
            'type': 'add',  # allocation
            'employee_id': self.employee.id,
            'holiday_status_id': self.leave_status.id,
            'type': 'add',
            'holiday_type': 'employee',
        })
        leaves_after = self.env['hr.holidays'].search_count(
            [('employee_id', '=', self.employee.id)])
        self.assertEqual(leaves_after, leaves_before + 1)
