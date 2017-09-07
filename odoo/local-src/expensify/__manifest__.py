{
    'name': 'Expensify',
    'category': 'Expenses',
    'description': """
    Import expenses from Expensify
""",
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/expensify.xml',
        'views/expensify_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}
