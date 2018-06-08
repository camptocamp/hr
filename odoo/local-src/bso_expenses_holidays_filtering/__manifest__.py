{
    'name': 'BSO Expenses Holidays Filtering',
    'description': 'BSO Expenses Holidays Filtering',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['hr_holidays', 'hr_expense'],
    'data': [
        'views/hr_expense.xml',
        'views/hr_holidays.xml',
    ],
    'installable': True,
    'auto_install': False,
}
