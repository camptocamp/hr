{
    'name': 'BSO restrict attachments visibility',
    'description': 'restrict access to attachments based on group users',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/attachment_security.xml'
    ],
    'application': False,
}
