{
    'name': 'BSO Track Subtype',
    'category': 'mail',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'mail'],
    # ,'sale', 'bso_dealsheet', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_message_subtype.xml'
    ],
    # 'demo': [
    #     'demo/demo_data.xml',
    # ],
    'application': False,
}
