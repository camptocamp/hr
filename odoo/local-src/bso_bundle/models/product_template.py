from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    seller_ids = fields.One2many(
        copy=True  # Copy Vendors on duplicate
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )
    is_bundle = fields.Boolean(
        string='Is Bundle'
    )
    is_epl = fields.Boolean(
        string='Is EPL'
    )
    nrc_product = fields.Many2one(
        string='NRC',
        comodel_name='product.product'
    )
    products = fields.Many2many(
        string='Products',
        comodel_name='product.product'
    )

    @api.onchange('is_bundle')
    def onchange_is_bundle(self):
        for rec in self:
            if rec.is_bundle:
                rec.update({
                    'recurring_invoice': True
                })
