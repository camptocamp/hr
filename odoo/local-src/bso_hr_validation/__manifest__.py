{
    'name': 'BSO HR Validation',
    'category': 'HR',
    'description': 'BSO specific Leaves & Expenses validation + date',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'hr_expense',
        'hr_holidays',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_expense_sheet.xml',
        'views/hr_holidays.xml',
    ],
    'installable': True,
    'auto_install': False,
}
