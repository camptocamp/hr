# -*- coding: utf-8 -*-
# Author: Damien Crier, Alexandre Fayolle
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Specific HR',
 'summary': 'Specific HR rules for BSO',
 'version': '9.0.1.0.0',
 'category': 'HR',
 'version': '1.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': ['hr',
             'hr_contract',
             'users_ldap_populate',
             'specific_fct',
             ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'security/res_groups.xml',
     'security/ir.model.access.csv',
     'security/hr_confidential/ir.model.access.csv',
     'views/hr_contract.xml',
     'views/hr_employee.xml',
     'views/hr_contract_category.xml',
     'views/hr_syntec_position.xml',
     'views/hr_employee_family.xml',
 ],
 'installable': True,
 }
