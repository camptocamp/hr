# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "BSO specific reports module",
    "version": "10.0.1.0.0",
    "depends": [
        'sale',
        'report',
        'account_payment_partner',
    ],
    "author": "Camptocamp SA",
    "website": "http://www.camptocamp.com",
    "license": "AGPL-3",
    "category": "Sale",
    "data": [
        'templates/layouts.xml',
        'templates/customer_invoice.xml',
    ],
    'installable': True,
}
