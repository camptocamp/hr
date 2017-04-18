# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Specific security',
 'summary': "Specific security for BSO",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': ['hr',
             'hr_holidays',
             'hr_expense',
             'hr_timesheet_sheet',
             'hr_timesheet_attendance',
             'project',
             'analytic',
             'sale',
             'stock',
             'purchase',
             'sales_team',
             'account',
             'analytic',
             'project',
             'survey',
             'specific_hr',
             'specific_product',
             'connector',
             'sale_contract',
             'base_technical_features',
             'marketing_campaign',
             'website',
             'product',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['data/hr_department_no_company.sql',
          'data/ir_rule.xml',
          'data/ir_rule.yml',
          'security/group.xml',
          ],
 'demo': [
     'demo/currency.sql',
     'demo/res.company.csv',
     'demo/product.category.csv',
     'demo/product.product.csv',
     'demo/users.xml',
     'demo/department.xml',
     'demo/add_home.xml',
     'demo/employee.xml',
     'demo/department_managers.xml',
 ],
 'test': ['test/account_minimal_test.xml'],
 'installable': True,
 }
