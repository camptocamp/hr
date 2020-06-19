{
    'name': 'BSO Subscription Lines',
    'category': 'sale',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale_contract', 'sale_contract_tax_subscription'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_subscription_line.xml'
    ],
    'application': False,
}
