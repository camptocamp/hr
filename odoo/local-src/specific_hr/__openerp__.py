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
             ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'views/hr_contract.xml',
 ],
 'installable': True,
 }
