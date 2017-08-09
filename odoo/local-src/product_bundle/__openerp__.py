{
    'name': 'Product Bundle',
    'category': 'Sales',
    'description': """
    Bundle Product of products
""",
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale', 'purchase', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/bundle_details.xml',
        'views/bundle_details_epl.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/sale_order_line.xml',
    ],
    'installable': True,
    'auto_install': False,
}
