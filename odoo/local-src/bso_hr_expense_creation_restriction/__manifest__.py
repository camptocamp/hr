{
    'name': 'HR restrict expense creation',
    'category': 'HR',
    'description': "Prevent expense creation in q different company than the employee's",
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'application': False,
}
