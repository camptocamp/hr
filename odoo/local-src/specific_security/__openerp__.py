# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Specific security',
 'summary': "Specific security for BSO",
 'version': '1.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': ['hr',
             'hr_holidays',
             'hr_expense',
             'project',
             'analytic',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['data/hr_department_no_company.sql',
          'data/ir_rule.xml',
          'data/ir_rule.yml',
          ],
 'installable': True,
 }
