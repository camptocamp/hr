{
    'name': 'Subscription Cease',
    'category': 'sale',
    'description': 'Allow cease of a subscription line',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['bso_sales_process', 'sales_team', 'purchase'],
    'data': [
        'views/sale_subscription.xml',
        'views/replace_subscription_line_wizard.xml',
        'security/ir.model.access.csv',
        'views/cease_order.xml'
    ],
    'application': False,
}
