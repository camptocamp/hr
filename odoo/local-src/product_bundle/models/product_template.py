from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_bundle = fields.Boolean(
        string='Is Bundle'
    )
    is_bundle_epl = fields.Boolean(
        string='Is Bundle EPL'
    )
    products = fields.One2many(
        string='Products',
        comodel_name='bundle.product',
        inverse_name='bundle_id'
    )
    epl_products_bundle_id = fields.Many2one(
        string='EPL Products Bundle',
        comodel_name='product.product'
    )
    bundle_upfront_uom_id = fields.Many2one(
        string='NRC Unit of Measure',
        comodel_name='product.uom'
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )

    @api.onchange('is_bundle')
    def onchange_is_bundle(self):
        for rec in self:
            rec.update({
                'is_bundle_epl': False
            })
