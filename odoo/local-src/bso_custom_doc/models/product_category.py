# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    terms_title = fields.Char(
        string='Terms title')
    terms_text = fields.Html(
        string='Terms content')
