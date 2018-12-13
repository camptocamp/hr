# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{'name': 'Specific sales',
 'summary': "Triple validation workflow",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp,Odoo Community Association (OCA)',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'depends': [
     'account',
     'bso_base',
     'sale_double_validation',
     'specific_security',
     'website_contract',
     'sale_contract',
     'account_invoice_merge',
     'account_payment_partner',
     'base_report_to_printer',
     'bso_webservice',
 ],
 'website': 'www.camptocamp.com',
 'demo': [
     'data/prep_exising_data.yml',
 ],
 'data': [
     'wizard/sale_refusal_view.xml',
     'wizard/mrp_invoicing_view.xml',
     'wizard/picking_update_delivery_date.xml',
     'views/partner.xml',
     'views/sale.xml',
     'views/sale_order_line.xml',
     'views/account_invoice.xml',
     'views/report_invoice.xml',
     'views/sale_subscription_views.xml',
     'views/product.xml',
     'views/stock_picking.xml',
 ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
