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
        'data/expensify_data.xml',
        'security/ir.model.access.csv',
        'views/expensify.xml',
        'views/expensify_expense.xml',
        'views/expensify_wizard.xml',
        'views/product_product.xml',
    ],
    'installable': True,
    'auto_install': False,
}
