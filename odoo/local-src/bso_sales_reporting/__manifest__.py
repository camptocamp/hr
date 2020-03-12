{
    'name': 'BSO Sales Reporting',
    'description': 'Sales Reporting',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'sale',
        'sale_contract',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
