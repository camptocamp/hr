# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Specific Product',
 'summary': "Specific fields for BSO",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': ['base',
             'product',
             'sale',
             'account',
             'stock',
             'sales_team',
             'website_contract',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['security/groups.xml',
          'security/ir.model.access.csv',
          'views/sale_order.xml',
          'views/product.xml',
          'views/account_invoice.xml',
          'views/network.xml',
          'views/res_company.xml',
          'views/product_uom_categ.xml',
          'views/product_uom.xml'
          ],
 'installable': True,
 }
