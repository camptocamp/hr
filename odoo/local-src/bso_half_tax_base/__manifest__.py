{
    'name': 'BSO half tax base',
    'category': 'accounting',
    'description': 'Half taxes must include full amount in base for subsequent taxes',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax.xml',
    ],
    'application': False,
}
