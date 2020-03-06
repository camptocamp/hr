{
    'name': 'Hr Contract Raise',
    'category': 'HR',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['hr_contract', 'specific_hr'],
    'data': [
        'views/hr_contract_form.xml',
        'views/hr_contract_raise_view.xml',
        #'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],
    'application': False,
}
