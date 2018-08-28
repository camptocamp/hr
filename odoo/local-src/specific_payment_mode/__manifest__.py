# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Specific payment_mode for BSO',
    'version': '10.0.1.0.0',
    'author': 'Camptocamp SA',
    'maintainer': 'Camptocamp SA',
    'license': 'AGPL-3',
    'depends': [
        'account_payment_sale',
        'specific_sale',
        'hr',
    ],
    'website': 'www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_subscription_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
