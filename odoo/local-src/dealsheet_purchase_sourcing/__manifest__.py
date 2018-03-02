# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Dealsheet Purchase Procurement',
    'summary': """TODO.""",
    'version': '10.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'bso_dealsheet',
        'purchase',
        'specific_product',
    ],
    'data': [
        'views/sale_dealsheet.xml',
        'wizards/wiz_sale_dealsheet_source.xml',
    ],
}
