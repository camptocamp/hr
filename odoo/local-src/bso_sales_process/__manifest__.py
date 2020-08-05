{
    'name': 'BSO Sales Process',
    'description': 'Sales Process',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['website_contract',
                'sale_contract',
                'bso_dealsheet',
                'sale_stock',
                'bso_sales_reporting',
                'bso_bundle',
                'sale'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/replace_subscription_lines_wizard.xml',
        'views/sale_subscription.xml',
        'views/sale_order_tree_view.xml',
        'views/sale_order_form_renewal.xml',
        'views/sale_order_form.xml'
    ],
    'application': False,
    'installable': True,
}
