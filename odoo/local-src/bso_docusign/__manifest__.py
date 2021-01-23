{
    'name': 'BSO Docusign',
    'category': '',
    'description': '',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'sale', 'docusign', 'bso_dealsheet'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/docusign_cron.xml',
        'views/docusign_document.xml',
        'views/docusign_wizard.xml',
        'views/docusign_anchor.xml',
        'views/docusign_template.xml',
        'views/menus.xml',
        'data/docusign_document_data.xml'
    ],
    'application': False,
}
