{
    'name': 'HR new employee',
    'category': 'HR',
    'description': 'Create new employees on AD',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'specific_hr'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_new_employee.xml',
        'data/ir_cron.xml',
        'data/res_api_records.xml',
    ],
    'application': False,
}
