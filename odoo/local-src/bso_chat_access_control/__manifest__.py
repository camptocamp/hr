{
    'name': 'Chat access control',
    'category': '',
    'description': 'Bypass odoo security to give write access to a '
                   'module chatter',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_model.xml',
        'views/ir_model_access.xml',
        'views/res_groups.xml',
    ],
    'application': False,
}
