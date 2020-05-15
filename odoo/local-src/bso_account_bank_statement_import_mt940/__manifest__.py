{
    'name': 'BSO Account Bank Statement Import MT940',
    'category': 'account',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'account', 'account_bank_statement_import_mt940'],
    'data': [
        'security/ir.model.access.csv',
        'data/import_mt940_files.xml',
        'views/account_config_settings.xml',
        'views/mt940_file.xml'
    ],
    'application': False,
}
