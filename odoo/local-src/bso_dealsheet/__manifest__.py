{
    'name': 'BSO Dealsheet',
    'category': 'Sale',
    'description': 'BSO Dealsheet Costs, Margins & Validation Process',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'sale',
        'product_bundle',
        'specific_sale',
        'bso_backbone',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_dealsheet.xml',
        'views/sale_dealsheet_line.xml',
        'views/sale_dealsheet_summary_line.xml',
        'views/sale_dealsheet_wizard_confirm.xml',
        'views/sale_dealsheet_wizard_refuse.xml',
        'views/sale_dealsheet_wizard_request.xml',
        'views/sale_order.xml',
        'wizard/wiz_sale_dealsheet_source.xml',
    ],
    'installable': True,
    'auto_install': False,
}
