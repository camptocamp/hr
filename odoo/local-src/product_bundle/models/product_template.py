from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_bundle = fields.Boolean(
        string='Is Bundle'
    )
    is_bundle_epl = fields.Boolean(
        string='Is Bundle EPL'
    )
    epl_products_bundle_id = fields.Many2one(
        string='EPL Products Bundle',
        comodel_name='product.product'
    )
    products = fields.One2many(
        string='Products',
        comodel_name='bundle.product',
        inverse_name='bundle_id'
    )

    @api.onchange('is_bundle')
    def onchange_is_bundle(self):
        for rec in self:
            rec.is_bundle_epl = False

    @api.onchange('is_bundle_epl')
    def onchange_is_bundle_epl(self):
        for rec in self:
            rec.epl_products_bundle_id = False
