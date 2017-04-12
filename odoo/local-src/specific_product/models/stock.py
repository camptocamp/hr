# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char(size=32)
