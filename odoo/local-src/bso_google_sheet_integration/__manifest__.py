{
    'name': 'Reports',
    'category': 'reports',
    'description': 'Display data from odoo in a google sheet, '
                   'and visualize it',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/record_to_spreadsheet.xml',
        'views/actions/act_window.xml',
        'views/menus/menuitem.xml',
        'views/google_sheet_workbook_view.xml',
        'views/google_sheet_settings_view.xml',
    ],
    "external_dependencies": {"python": ["hyou"]},
    'application': True,
}
