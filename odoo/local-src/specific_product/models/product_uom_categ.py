# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductUomCateg(models.Model):
    _inherit = 'product.uom.categ'

    recurring = fields.Boolean(
        default=False,
        string='Recurring')
