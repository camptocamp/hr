# -*- coding: utf-8 -*-
# © 2016 Camptocamp (alexandre.fayolle@camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Specific HR for BSO',
    'version': '10.0.1.0.0',
    'category': 'HR',
    'license': 'AGPL-3',
    'summary': 'Specific HR rules for BSO',
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'depends': [
        'hr_contract',
        ],
    'data': [
        'views/hr_contract.xml',
    ],
    'installable': True,
}
