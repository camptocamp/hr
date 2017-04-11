# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "RocTool specific sale module",
    "version": "10.0.1.0.0",
    "depends": [
        'specific_crm',
        'sale',
        'sale_crm',
        'sales_team',
        'sale_timesheet',
        'website_sale_options',
        'mrp',
    ],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "http://www.camptocamp.com",
    "license": "GPL-3 or any later version",
    "category": "Sale",
    "data": [
        'views/product_views.xml',
        'views/sale_order_crm.xml',
        'views/project_task.xml',
        'views/mrp_bom.xml',
        'data/res_groups_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
