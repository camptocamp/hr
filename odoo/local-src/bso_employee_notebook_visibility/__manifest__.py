{
    'name': 'BSO Employee Notebook Visibility',
    'description': 'Only display employee personal data to HR Manager',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'hr',
        'hr_family',
    ],
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
    'auto_install': False,
}
