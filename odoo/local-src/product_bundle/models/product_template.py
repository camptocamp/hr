from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_bundle = fields.Boolean(string='Is Product Bundle')
    products = fields.One2many(string='Products',
                               comodel_name='bundle.product',
                               inverse_name='bundle_id')
