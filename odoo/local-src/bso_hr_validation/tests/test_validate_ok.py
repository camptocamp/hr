from odoo.exceptions import ValidationError
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestValidateOk(common.TransactionCase):
    def setUp(self):
        super(TestValidateOk, self).setUp()
        self.classic_validator = self._create_employee("Classic Validator")
        self.self_validator = self._create_employee("Self Validator", True)
        self.holiday_status = self._create_holiday_status()

    def _create_employee(self, name, is_self_validator=False):
        return self.env['hr.employee'].create({
            'name': name,
            'user_id': self._create_user(name, is_self_validator).id,
        })

    def _create_user(self, name, is_self_validator):
        groups_id = [
            self.env.ref('hr_expense.group_hr_expense_user').id,
            self.env.ref('hr_holidays.group_hr_holidays_user').id,
        ]
        if is_self_validator:
            groups_id.append(
                self.env.ref('bso_hr_validation.group_self_validator').id
            )
        return self.env['res.users'].create({
            'name': name,
            'login': name,
            'email': name,
            'groups_id': [[6, 0, groups_id]],
        })

    def _create_holiday_status(self):
        return self.env['hr.holidays.status'].create({
            'name': 'Test Status',
        })

    def _create_holiday(self, employee_id):
        return self.env['hr.holidays'].create({
            'employee_id': employee_id.id,
            'holiday_status_id': self.holiday_status.id,
            'type': 'add',
            'holiday_type': 'employee',
            'date_from': '2019-01-04',
            'date_to': '2019-01-05',
        })

    def _create_expense(self, employee_id):
        return self.env['hr.expense.sheet'].create({
            'employee_id': employee_id.id,
            'name': 'Test Expense',
        })

    def _test_holiday(self, employee, manager):
        holiday = self._create_holiday(employee).sudo(user=manager.user_id)
        holiday.action_validate()
        holiday.action_refuse()

    def test_holiday(self):
        self._test_holiday(self.classic_validator, self.self_validator)
        self._test_holiday(self.self_validator, self.classic_validator)
        with self.assertRaises(ValidationError):
            self._test_holiday(self.classic_validator, self.classic_validator)
        self._test_holiday(self.self_validator, self.self_validator)

    def _test_expense(self, employee, manager):
        expense = self._create_expense(employee).sudo(user=manager.user_id)
        expense.approve_expense_sheets()
        expense.refuse_expenses("Test Reason")

    def test_expense(self):
        self._test_expense(self.classic_validator, self.self_validator)
        self._test_expense(self.self_validator, self.classic_validator)
        with self.assertRaises(ValidationError):
            self._test_expense(self.classic_validator, self.classic_validator)
        self._test_expense(self.self_validator, self.self_validator)
