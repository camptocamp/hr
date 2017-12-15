{
    'name': 'BSO Dealsheet',
    'category': 'Sale',
    'description': 'BSO Dealsheet Costs, Margins & Validation Process',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale', 'product_bundle'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_dealsheet.xml',
        'views/sale_dealsheet_line.xml',
        'views/sale_dealsheet_summary_line.xml',
        'views/sale_dealsheet_wizard.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}
