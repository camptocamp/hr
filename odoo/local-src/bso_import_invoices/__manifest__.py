{
    'name': 'BSO Import Invoices',
    'category': 'Accounting',
    'description': 'Import account invoices from ubersmith',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        'security/bso_import_invoices_security.xml',
        'security/ir.model.access.csv',
        'views/ubersmith_settings.xml',
        'views/ubersmith_brand.xml',
        'views/ubersmith_client.xml',
        'views/ubersmith_currency.xml',
        'views/ubersmith_service_plan.xml',
        'views/ubersmith_invoice.xml',
        'views/ubersmith_invoice_line.xml',
        'views/ubersmith_tax.xml',
        'views/ubersmith_service.xml',
        'views/ubersmith_menus.xml',
        'data/bso_import_invoices_data.xml'
    ],
    'application': False,
}
