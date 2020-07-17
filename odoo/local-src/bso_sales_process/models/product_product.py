from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    mergeable = fields.Boolean(
        string='Mergeable',
        default=True,
        copy=True
    )
