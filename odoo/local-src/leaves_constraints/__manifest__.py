{
    'name': 'Leaves Constraints',
    'category': 'Leaves',
    'description': 'Prevent users from self-approving & self-refusing leaves',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays.xml',
    ],
    'installable': True,
    'auto_install': False,
}
