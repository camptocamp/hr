{
    'name': 'BSO Mailchimp',
    'description': 'BSO Mailchimp',
    'author': 'BSO',
    'website': 'https://www.bsonetwork.com',
    'depends': ['base', 'crm', 'specific_crm'],
    'data': [
        "security/bso_mailchimp_security.xml",
        'security/ir.model.access.csv',
        "views/mailchimp_campaign.xml",
        "views/mailchimp_list_member_stats.xml",
        "views/crm_lead.xml",
        "views/mailchimp_settings_view.xml",
        "views/mailchimp_list_segment.xml",
        "views/mailchimp_list.xml",

    ],
    "external_dependencies": {"python": ["mailchimp3"]},
    'installable': True,
    'auto_install': False,
}
