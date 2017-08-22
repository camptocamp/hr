# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{'name': 'Bso specific purchase',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp SA',
 'maintainer': 'Camptocamp SA',
 'license': 'AGPL-3',
 'depends': [
     'bso_base',
     'purchase',
     'specific_product',
 ],
 'website': 'www.camptocamp.com',
 'data': [
     'views/partner.xml',
     'views/purchase_order.xml',
     'data/ir_cron.xml',
 ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
