{
    'name': 'BSO Sales Commissions',
    'description': 'Sales Commissions',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sales_team', 'sale', 'purchase', 'bso_dealsheet'],
    'data': [
        'security/bso_sales_commission_security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/sale_target_view.xml',
        'views/salesperson_commission_line.xml',
        'views/salesperson_commission_quarter.xml',
        'views/sales_commission_settings.xml',

    ],
    'qweb': [
        'static/src/xml/SalesDashboard.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
