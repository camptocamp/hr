from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expensify_category_id = fields.Many2one(
        string='Expensify Category',
        comodel_name='expensify.category'
    )
