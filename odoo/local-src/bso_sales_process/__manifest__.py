{
    'name': 'BSO Sales Process',
    'description': 'Sales Process',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['website_contract',
                'sale_contract',
                'bso_dealsheet',
                'bso_pop_up_message',
                'sale_stock',
                'bso_sales_reporting',
                'bso_bundle',
                'sale'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/so_cancellation_view.xml',
        'views/subscription_form_new_buttons.xml',
        'views/sale_order_tree_view.xml',
        'views/sale_order_form_renewal.xml',
    ],
    'application': False,
    'installable': True,
}
