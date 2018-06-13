# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'BSO Accounting',
    'description': 'Specific accounting for BSO',
    'author': 'camptocamp',
    'website': 'https://camptocamp.com',
    'depends': [
        'account',
        'account_invoice_merge',
        'account_payment_partner',
    ],
    'data': [
        'views/invoice_merge_wizard.xml',
    ],
    'application': True,
}
