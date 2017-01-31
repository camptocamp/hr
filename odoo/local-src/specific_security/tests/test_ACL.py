# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import AccessError
from openerp.tests import common


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
        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
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
        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
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
        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
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
        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
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
        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
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

        leave_allocation.sudo(user=self.melanie).signal_workflow('validate')
        self.assertEquals(leave_allocation.state, 'validate')
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.emmanuel.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        # next instruction must fail
        with self.assertRaises(AccessError):
            leave_request = self.env['hr.holidays'].sudo(
                user=self.emmanuel).create(vals)
        leave_request = self.env['hr.holidays'].sudo(
            user=self.melanie).create(vals)
        self.assertTrue(leave_request)
        leave_request.sudo(user=self.melanie).signal_workflow('validate')
        self.assertEquals(leave_request.state, 'validate')
