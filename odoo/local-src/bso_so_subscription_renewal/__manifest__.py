{
    'name': 'Sale Subscription Renewal',
    'category': 'sale',
    'description': 'Prevent subscription update untill the sale line is '
                   'delivered',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'base',
        'sale',
        'sale_contract',
        'sale_stock',
        'bso_dealsheet',
        'specific_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_update_subscription_button.xml',
        'views/sale_order_remove_lock_button.xml'
    ],
    'application': False,
}
