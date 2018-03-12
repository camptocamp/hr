# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{'name': 'Specific mailchimp models for BSO',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp SA',
 'maintainer': 'Camptocamp SA',
 'license': 'AGPL-3',
 'depends': [
     'crm',
 ],
 'website': 'www.camptocamp.com',
 'data': [
     "views/crm_mailchimp_campaign.xml",
     "views/crm_mailchimp_mailing.xml",
     "views/crm_mailchimp_mailing_stats.xml",
     "wizard/create_campaign_wizard.xml",
     "security/ir.model.access.csv",
 ],
 'test': [],
 'installable': True,
 }
