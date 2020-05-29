{
    'name': 'BSO Supplier Dispute',
    'category': 'account',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sh_supplier_dispute'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice.xml'
    ],
    'application': False,
}
