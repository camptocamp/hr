# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    group_supplier_invoice = fields.Boolean(
        string='Group Supplier Invoice',
        help='Group supplier invoices monthly / quarterly / yearly'
    )
    automatic_supplier_invoicing = fields.Boolean(
        string='Automatic Supplier Invoicing',
        help='Create automatically invoices from purchase orders'
    )
    supplier_invoicing_period = fields.Selection(
        [('monthly', u"Monthly"),
         ('quarterly', u"Quarterly"),
         ('yearly', u"Yearly"),
         ],
        string=u"Supplier invoicing period",
        default='monthly')
    supplier_invoicing_mode = fields.Selection(
        [('end_of_term', u"End of term"),
         ('start_of_term', u"Start of term"),
         ],
        string=u"Supplier invoicing mode",
        default='end_of_term')
