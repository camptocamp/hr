{
    'name': 'BSO HR Holidays Report',
    'category': 'hr',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': [
        'base',
        'hr_holidays',
        'hr_holidays_compute_days',
        'specific_hr',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/hr_holidays_data.xml',
        'data/hr_holidays_report_data.xml',
        'views/hr_holidays.xml',
        'views/hr_holidays_report.xml',
        'views/hr_holidays_report_line.xml',
        'views/menuitem.xml',
    ],
    'application': True,
}
