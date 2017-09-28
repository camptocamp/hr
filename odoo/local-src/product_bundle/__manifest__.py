{
    'name': 'Product Bundle',
    'category': 'Sales',
    'description': """
    BSO Bundles + EPL
""",
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale', 'purchase', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/bundle_details.xml',
        'views/bundle_details_epl.xml',
        'views/epl_cable.xml',
        'views/epl_device.xml',
        'views/epl_link.xml',
        'views/epl_pop.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}
