from openerp import api, fields, models


class Bundle(models.Model):
    _inherit = 'product.template'

    is_bundle = fields.Boolean(string='Is Product Bundle')
    default_products = fields.Many2many('product.product', string='Products')
