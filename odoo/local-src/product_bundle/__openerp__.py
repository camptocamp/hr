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
        'views/bundle.xml',
        'views/bundle_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
}
