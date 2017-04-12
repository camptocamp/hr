# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrc = fields.Float()
    is_epl = fields.Boolean(default=False)
