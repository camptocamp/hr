# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    def test_rh_002_create_allocation_same_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST same company',
             'company_id': self.melanie.company_id.id})
        self.assertTrue(req)

    def test_rh_003_create_allocation_other_company(self):
        req = self.env['hr.holidays.status'].sudo(user=self.melanie).create(
            {'name': 'TEST other company',
             'company_id': self.env.ref('base.main_company').id})
        self.assertTrue(req)

    def test_rh_004_create_allocation_same_company_and_other_empl_take(self):
        leave_type = self.env['hr.holidays.status'].sudo(
            user=self.melanie).create(
                {'name': 'TEST same company',
                 'company_id': self.melanie.company_id.id,
                 'annual_leaves': 25.})
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.andre.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        leave_request = self.env['hr.holidays'].sudo(
            user=self.andre).create(vals)
        self.assertTrue(leave_request)

    def test_rh_005_create_allocation_other_company_and_other_empl_take(self):
        leave_type = self.env['hr.holidays.status'].sudo(
            user=self.melanie).create(
                {'name': 'TEST same company',
                 'company_id': self.env.ref('base.main_company').id,
                 'annual_leaves': 25.})
        vals = {'holiday_status_id': leave_type.id,
                'employee_id': self.andre.id,
                'date_from': '2017-05-11 07:00:00',
                'date_to': '2017-05-12 19:00:00'
                }
        leave_request = self.env['hr.holidays'].sudo(
            user=self.andre).create(vals)
        self.assertTrue(leave_request)
