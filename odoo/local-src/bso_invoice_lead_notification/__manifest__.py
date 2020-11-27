{
    'name': 'Invoices & leads; user notifications',
    'category': 'notification',
    'description': 'Prevent unwanted notification from invoices, and leads',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['account', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_form.xml'
    ],
    'application': False,
}
