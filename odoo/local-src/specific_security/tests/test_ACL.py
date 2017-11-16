# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import common


class TestACL(common.TransactionCase):

    def setUp(self):
        super(TestACL, self).setUp()
        self.melanie = self.env.ref('specific_security.demo_melanie')
        self.emmanuel = self.env.ref('specific_security.demo_emmanuel')
        self.andre = self.env.ref('specific_security.demo_andre')
        self.damien = self.env.ref('specific_security.demo_damien')

        self.emp_melanie = self.env.ref('specific_security.emp_melanie')
        self.emp_emmanuel = self.env.ref('specific_security.emp_epelle')
        self.emp_andre = self.env.ref('specific_security.emp_andre')
        self.emp_damien = self.env.ref('specific_security.emp_damien')

        test_users = self.env['res.users']
        test_users |= self.emmanuel
        test_users |= self.damien
        test_users |= self.andre
        self.test_users = test_users

    def test_rh_001_employee_see_manager(self):
        self.assertEquals(
            self.emp_melanie.sudo(user=self.melanie).parent_id.name,
            self.emp_emmanuel.name
        )
        self.assertEquals(
            self.emp_melanie.sudo(user=self.melanie).parent_id.user_id.name,
            self.emmanuel.name
        )

    def test_rh_002_create_leave_type_same_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST same company',
             'company_id': self.melanie.company_id.id})
        self.assertTrue(req)

    def test_rh_003_create_leave_type_other_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST other company',
             'company_id': self.env.ref('base.main_company').id})
        self.assertTrue(req)

    def test_rh_004_create_leave_type_and_allocation_same_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST same company',
             'company_id': self.melanie.company_id.id})
        self.assertTrue(req)
        vals = {'holiday_status_id': req.id,
                'employee_id': self.andre.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }
        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)
        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')

    def test_rh_005_create_leave_type_and_allocation_other_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST same company',
             'company_id': self.env.ref('base.main_company').id})
        self.assertTrue(req)
        vals = {'holiday_status_id': req.id,
                'employee_id': self.andre.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }
        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)
        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')

    def test_rh_006_create_leave_type_and_allocation_other_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST same company',
             'company_id': self.env.ref('base.main_company').id})
        self.assertTrue(req)
        vals = {'holiday_status_id': req.id,
                'employee_id': self.emmanuel.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }
        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)
        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')

    def test_rh_007_create_leave_type_same_company_and_other_empl_take(self):
        leave_type = self.env['hr.holidays.status'].sudo(
            user=self.melanie).create(
                {'name': 'TEST same company',
                 'company_id': self.melanie.company_id.id})
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.andre.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }
        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)
        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.andre.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        leave_request = self.env['hr.holidays'].sudo(
            user=self.andre).create(vals)
        self.assertTrue(leave_request)

    def test_rh_008_create_leave_type_same_company_and_other_empl_take(self):
        leave_type = self.env['hr.holidays.status'].sudo(
            user=self.melanie).create(
                {'name': 'TEST same company',
                 'company_id': self.melanie.company_id.id})
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.emmanuel.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }
        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)
        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.emmanuel.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        leave_request = self.env['hr.holidays'].sudo(
            user=self.emmanuel).create(vals)
        self.assertTrue(leave_request)

    def test_rh_009_create_leave_type_same_company_and_other_empl_take(self):
        leave_type = self.env['hr.holidays.status'].sudo(
            user=self.melanie).create(
                {'name': 'TEST same company',
                 'company_id': self.melanie.company_id.id})
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.emmanuel.id,
                'number_of_days_temp': 25.,
                'type': 'add',
                }

        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)

        leave_allocation = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_allocation)

        leave_allocation.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_allocation.state, 'validate')
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.emmanuel.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        # next instruction must fail

        leave_request = self.env['hr.holidays'].sudo(
            user=self.emmanuel).create(vals)
        # leave_request = self.env['hr.holidays'].sudo(
        #     user=self.melanie).create(vals)
        self.assertTrue(leave_request)
        leave_request.sudo(user=self.melanie).action_validate()
        self.assertEquals(leave_request.state, 'validate')

    def test_create_leave_type(self):
        for company in self.env['res.company'].search([]):
            vals = {'name': 'TEST same company',
                    'company_id': company.id}
            if company in self.melanie.company_ids:
                req = self.env['hr.holidays.status'].sudo(
                    user=self.melanie).create(vals)
                self.assertTrue(req)
            else:
                with self.assertRaises(AccessError):
                    req = self.env['hr.holidays.status'].sudo(
                        user=self.melanie).create(vals)

    def test_create_leave_allocation(self):
        leaves_types = {}
        for company in self.melanie.company_ids:
            vals = {'name': 'TEST company',
                    'company_id': company.id}
            if company in self.melanie.company_ids:
                leaves_types[company.id] = self.env['hr.holidays.status'].sudo(
                    user=self.melanie).create(vals)
        self.assertEquals(len(leaves_types), 6)

        for employee in self.env['hr.employee'].search([]):
            vals = {
                'holiday_status_id': leaves_types[employee.company_id.id].id,
                'employee_id': employee.id,
                'number_of_days_temp': 25.,
                'type': 'add',
            }
            leave_allocation = self.env['hr.holidays'].sudo(
                user=self.melanie).create(vals)
            self.assertTrue(leave_allocation)

    def test_create_leave_request(self):
        leaves_types = {}
        for company in self.melanie.company_ids:
            vals = {'name': 'TEST company',
                    'company_id': company.id}
            if company in self.melanie.company_ids:
                leaves_types[company.id] = self.env['hr.holidays.status'].sudo(
                    user=self.melanie).create(vals)
        self.assertEquals(len(leaves_types), 6)
        emp_obj = self.env['hr.employee']
        for employee in emp_obj.search([('user_id', '!=', False)]):
            vals = {
                'holiday_status_id': leaves_types[employee.company_id.id].id,
                'employee_id': employee.id,
                'number_of_days_temp': 25.,
                'type': 'add',
            }
            leave_allocation = self.env['hr.holidays'].sudo(
                user=self.melanie).create(vals)
            self.assertTrue(leave_allocation)
            leave_allocation.sudo(
                user=self.melanie).action_validate()

        for employee in emp_obj.search([('user_id', '!=', False)]):
            vals = {
                'holiday_status_id': leaves_types[employee.company_id.id].id,
                'employee_id': employee.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
            }
            leave_request = self.env['hr.holidays'].sudo(
                user=employee.user_id).create(vals)
            self.assertTrue(leave_request)

    def test_validate_subordinates_holidays(self):
        leaves_types = {}
        for company in self.melanie.company_ids:
            vals = {'name': 'TEST company',
                    'company_id': company.id}
            if company in self.melanie.company_ids:
                leaves_types[company.id] = self.env['hr.holidays.status'].sudo(
                    user=self.melanie).create(vals)
        self.assertEquals(len(leaves_types), 6)
        emp_obj = self.env['hr.employee']
        for employee in emp_obj.search([('user_id', 'in',
                                         self.test_users.ids)]):
            vals = {
                'holiday_status_id': leaves_types[employee.company_id.id].id,
                'employee_id': employee.id,
                'number_of_days_temp': 25.,
                'type': 'add',
            }
            leave_allocation = self.env['hr.holidays'].sudo(
                user=self.melanie).create(vals)
            self.assertTrue(leave_allocation)
            leave_allocation.sudo(
                user=self.melanie).action_validate()

        leaves_requests = []
        for employee in emp_obj.search([('user_id', 'in',
                                         self.test_users.ids)]):
            vals = {
                'holiday_status_id': leaves_types[employee.company_id.id].id,
                'employee_id': employee.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
            }
            leave_request = self.env['hr.holidays'].sudo(
                user=employee.user_id).create(vals)
            self.assertTrue(leave_request)
            leaves_requests.append(leave_request)

        for leave in leaves_requests:
            leave.sudo(user=self.melanie).action_validate()

    def test_create_expense(self):
        emp_obj = self.env['hr.employee']
        product_expense = self.env.ref('scen.expense_product_0013')
        for employee in emp_obj.search([('user_id', 'in',
                                         self.test_users.ids)]):
            product = product_expense.copy(
                {'company_id': employee.company_id.id}
            )
            vals = {
                'name': "Expense %s" % employee.name,
                'employee_id': employee.id,
                'product_id': product.id,
                'unit_amount': 123.45,
                'company_id': employee.company_id.id,
            }
            expense = self.env['hr.expense'].sudo(
                user=employee.user_id).create(vals)
            self.assertTrue(expense)
            expense.sudo(user=employee.user_id.id).submit_expenses()

    def test_create_expense_and_validate(self):
        emp_obj = self.env['hr.employee']
        product_expense = self.env.ref('scen.expense_product_0013')
        for employee in emp_obj.search([('user_id', 'in',
                                         self.test_users.ids)]):
            product = product_expense.copy(
                {'company_id': employee.company_id.id}
            )
            vals = {
                'name': "Expense %s" % employee.name,
                'employee_id': employee.id,
                'product_id': product.id,
                'unit_amount': 123.45,
                'company_id': employee.company_id.id,
            }
            expense = self.env['hr.expense'].sudo(
                user=employee.user_id).create(vals)
            self.assertTrue(expense)
            expense.sudo(user=employee.user_id.id).submit_expenses()
            user = self.melanie
            if employee.parent_id:
                user = employee.parent_id.user_id.id
            expense.sheet_id.sudo(user=user).approve_expense_sheets()
