# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "Odoo - Docusign Integration Digital Sign",
    "version": "10.0.0.0.1",
    "depends": ["sale"],
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": """
    Odoo Docusign integration
    Odoo Digital Signature
    """,
    "description": """
	Odoo Digital Signature with Docusign
    """,
    'data': [
            'security/ir.model.access.csv',
            'views/docusign_config_view.xml',
            'views/docusign_template_view.xml',
            'views/docusign_document_view.xml',
            'wizard/send_and_retrive_document_view.xml'
                   ],
    'images':['static/description/docubanner.png'],
    'external_dependencies': {"python": ["httplib2"]},
    'installable': True,
    'application': True,
    "sequence": 2,
    'price': 299,
    'currency': 'EUR'
}
