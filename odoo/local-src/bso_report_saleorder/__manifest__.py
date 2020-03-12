{
    'name': 'BSO Report Sale Order',
    'category': 'sale',
    'description': 'Custom Sale Order Report from Website quote',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'sale',
        'website_quote',
        'bso_sales_reporting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/bso_report_saleorder.xml'
    ],
    'application': False,
}
