# -*- coding: utf-8 -*-
{
    'name': 'Odoo Hubspot Integration',
    'version': '10.0',
    'category': 'Hubspot',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'summary': 'Integration of Odoo Partners with hubspot contacts',
    'description': """
Hubspot Integration
==========================
Odoo Partners are imported and updated from and to Hubspot.
Using Hubspot API data is synced.
<keywords>
Odoo Hubspot Integration App
Hubspot
odoo hubspot
odoo Hubspot connector
odoo Hubspot integration
hubspot crm
    """,
    'website': 'pragtech.co.in',
    'depends': [
        'base', 'base_setup', 'sale', 'crm', 'specific_crm',
        'bso_opportunities_reporiting'
    ],
    'data': [
        'security/bso_hubspot_security.xml',
        'security/ir.model.access.csv',
        'views/crm_lead.xml',
        'views/hubspot_scheduler.xml',
        'views/configSettings.xml',
        'views/crm_stage.xml'
    ],
    "external_dependencies": {
        "python": ["hubspot"]
    },
    'price': 349,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['images/hubspot-integration-animated.gif'],
    'live_test_url': """http://www.pragtech.co.in/company/proposal-form.html
    ?id=103&name=hubspot""",
    'application': True,
    'auto_install': False,
    'installable': True,
}
