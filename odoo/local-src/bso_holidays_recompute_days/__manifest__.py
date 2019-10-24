{
    'name': 'BSO holidays start end in workday',
    'category': 'Hr',
    'description': 'Prevent the user from saving/writing on a hr.holiday \
    that starts or end on a public holiday / rest day',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'hr_holidays', 'hr_holidays_compute_days'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'application': False,
}
