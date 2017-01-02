# -*- coding: utf-8 -*-
# Author: Damien Crier, Alexandre Fayolle
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Specific HR',
 'summary': 'Specific HR rules for BSO',
 'version': '9.0.1.0.0',
 'category': 'HR',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'depends': ['hr',
             'hr_contract',
             'hr_holidays_legal_leave',
             'users_ldap_populate',
             'specific_fct',
             'hr_holidays_compute_days',
             'hr_holidays_imposed_days',
             ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'security/res_groups.xml',
     'security/ir.model.access.csv',
     'security/hr_confidential/ir.model.access.csv',
     'data/leaves_allocation_update.xml',
     'views/hr_contract.xml',
     'views/hr_employee.xml',
     'views/hr_contract_category.xml',
     'views/hr_syntec_position.xml',
     'views/hr_employee_family.xml',
     'views/hr_holidays_status.xml',
     'views/hr_imposed_days.xml',
 ],
 'installable': True,
 }
