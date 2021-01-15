{
    'name': 'Subscription Cease',
    'category': 'sale',
    'description': 'Allow cease of a subscription line',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'bso_sales_process', 'sales_team', 'mail',
                'purchase'],
    'data': [
        'security/ir.model.access.csv',
        # views
        'views/sale_subscription.xml',
        'views/replace_subscription_line_wizard.xml',
        'views/cease_order.xml',
        'views/res_partner_form.xml',
        'views/res_company.xml',
        # data
        'data/cease_data.xml'
    ],
    'application': True,
}
