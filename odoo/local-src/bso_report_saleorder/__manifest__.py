{
    'name': 'BSO Report Sale Order',
    'category': 'sale',
    'description': 'Custom Sale Order Report from Website quote',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'base',
        'sale',
        'website_quote'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bso_report_saleorder.xml'
    ],
    'application': False,
}
