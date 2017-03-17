# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{'name': 'Specific sales',
 'summary': "Triple validation workflow",
 'version': '9.0.1.0.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'depends': [
     'sale_double_validation',
     'specific_security',
 ],
 'website': 'www.camptocamp.com',
 'data': [
     'wizard/sale_refusal_view.xml',
     'views/sale.xml',
 ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
