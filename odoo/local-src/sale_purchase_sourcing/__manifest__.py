# -*- coding: utf-8 -*-
# Author: Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale Purchase Procuremnt',
    'summary': """TODO.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'sale',
        'purchase',
        'specific_product',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/record_rules.xml',
        'wizards/wiz_sale_order_source.xml',
        'views/order_views.xml',
    ],
}
