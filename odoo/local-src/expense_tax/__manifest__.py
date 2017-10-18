{
    'name': 'Expense Tax',
    'category': 'Taxes',
    'description': 'Select & Manage expensable taxes',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'account', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax.xml',
        'views/hr_expense.xml',
    ],
    'installable': True,
    'auto_install': False,
}
