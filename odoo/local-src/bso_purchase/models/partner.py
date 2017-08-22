# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    group_supplier_invoice = fields.Boolean(
        string='Group Supplier Invoice',
        help='Group invoices monthly when is supplier'
    )
    automatic_supplier_invoicing = fields.Boolean(
        string='Automatic Supplier Invoicing',
        help='Create automatically invoices from purchase orders'
    )
