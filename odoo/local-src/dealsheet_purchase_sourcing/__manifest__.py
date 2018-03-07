# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

# This module is based on sale_purchase_sourcing module. In the future, we
# might want to extrapolate the base machinery to provide a mixin class to be
# inherited to sale.order, sale.dealsheet or any other model.
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
