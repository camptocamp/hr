{
    'name': 'Analytic Account Parents',
    'category': 'analytic',
    'description': 'Gives the possibility to link ACs and their subscription',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['analytic', 'sale_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_account_form_view.xml'
    ],
    'application': False,
}
