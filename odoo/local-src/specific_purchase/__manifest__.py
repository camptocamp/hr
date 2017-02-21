# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "RocTool specific Purchase Module",
    "version": "10.0.1.0.0",
    "depends": [
        'purchase',
        'stock',
    ],
    "category": "Purchase",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "http://www.camptocamp.com",
    "license": "GPL-3 or any later version",
    "data": [
        # security
        'security/ir.model.access.csv',
        # data
        'data/sequence.xml',
        # views
        'views/purchase_line_views.xml',
        'views/purchase_views.xml',
    ],
    'installable': True,
}
