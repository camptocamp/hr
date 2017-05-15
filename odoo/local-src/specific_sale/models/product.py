# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_ghost = fields.Boolean(
        string='Ghost Product',
    )


class ProuctCategory(models.Model):
    _inherit = 'product.category'

    engineering_validation_required = fields.Boolean(
        string='Engineering Validation Required',
    )
    system_validation_required = fields.Boolean(
        string='System Validation Required',
    )
    process_validation_required = fields.Boolean(
        string='Process Validation Required',
    )
