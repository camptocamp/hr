# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'Specific Product',
 'summary': "Specific fields for BSO",
 'version': '1.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': ['base',
             'product',
             'stock',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['views/sale_order.xml',
          'views/product.xml',
          # 'data/test_product_multi_variant.xml',
          # 'data/test_products.xml',
          ],
 'installable': True,
 }
