{
    'name': 'BSO Dealsheet',
    'category': 'sale',
    'description': 'Dealsheet Costs, Margins & Validation Process',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'sale',
        'purchase',
        'bso_backbone',
        'bso_bundle',
        'specific_sale',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/sale_dealsheet.xml',
        'views/sale_dealsheet_line.xml',
        'views/sale_dealsheet_wizard_confirm.xml',
        'views/sale_dealsheet_wizard_refuse.xml',
        'views/sale_dealsheet_wizard_request.xml',
        'views/sale_order.xml',
    ],
    'application': True,
}
