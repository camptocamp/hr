{
    'name': 'BSO restrict attachments visibility',
    'description': 'Restrict access to attachments based on group users',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/attachment_security.xml',
    ],
    'application': False,
}
