{
    'name': 'BSO Bundle',
    'category': 'Sale',
    'description': 'Bundle NRC/MRC Products & EPL',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'base',
        'sale',
        'product',
        'bso_backbone',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/bundle_details.xml',
        'views/bundle_details_epl.xml',
        'views/bundle_details_epl_link.xml',
        'views/bundle_details_product.xml',
        'views/optimal_api.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'application': False,
}
