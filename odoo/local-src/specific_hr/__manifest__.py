# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "RocTool Specific HR Module",
    "version": "10.0.1.0.0",
    "depends": [
        'hr',
        'hr_contract',
    ],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "http://www.camptocamp.com",
    "license": "GPL-3 or any later version",
    "category": "Sale",
    "data": [
        # data
        'data/employee_status_data.xml',
        # Views
        'views/employee_views.xml',
        'views/hr_contract_views.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
    ],
    'installable': True,
}
