{
    'name': 'BSO sale confirm',
    'category': 'sale',
    'description': 'Prevent sale order confirmation when on a different '
                   'comapny than the user\'s home company',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale', 'bso_pop_up_message'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'application': False,
}
