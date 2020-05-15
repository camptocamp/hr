# -*- coding: utf-8 -*-
{
    'name': "BSO update statement",
    'description': 'Possibility to merge existing statements, or update an'
                   'existing statement with the content of a csv ',
    'author': "BSO",
    'website': 'https://www.bsonetwork.com',

    'category': 'Accounting',
    'version': '0.1',

    'depends': ['account_bank_statement_import_csv'],

    'data': [
        'views/views.xml',
    ],
}
