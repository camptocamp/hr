# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{'name': 'Specific Crm',
 'summary': "Specific CRM for BSO",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'LGPL-3',
 'category': 'Others',
 'depends': [
     'crm',
     'sale',
     'web_enterprise',
 ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'templates/assets.xml',
     'views/crm_industry.xml',
     'views/crm_lead_quicktitle.xml',
     'views/crm_sources.xml',
     'views/crm.xml',
     'views/res_partner.xml',
     'security/ir.model.access.csv',
 ],
 'installable': True,
 }
