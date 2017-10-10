from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    expensify_category_id = fields.Many2one(
        string='Expensify Category',
        comodel_name='expensify.category'
    )
