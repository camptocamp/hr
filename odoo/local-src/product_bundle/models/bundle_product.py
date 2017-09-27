from odoo import fields, models


class BundleProduct(models.Model):
    _name = 'bundle.product'

    bundle_id = fields.Many2one(
        string='Bundle',
        comodel_name='product.template',
        ondelete='cascade',
        required=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True
    )
    uom_id = fields.Many2one(
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    quantity = fields.Integer(
        string='Default Quantity',
        default=0,
        required=True
    )
