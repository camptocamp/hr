from odoo import models, fields, api


class BundleDetailsProduct(models.Model):
    _name = 'bundle.details.product'

    bundle_details_id = fields.Many2one(
        string='Bundle Details',
        comodel_name='bundle.details',
        ondelete='cascade'
    )
    bundle_details_id_epl = fields.Many2one(
        string='Bundle Details EPL',
        comodel_name='bundle.details',
        ondelete='cascade'
    )
    bundle_categ_id = fields.Many2one(
        string='Bundle Category',
        comodel_name='product.category',
        required=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True
    )
    description = fields.Char(
        string='Description'
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True
    )
    uom_id = fields.Many2one(
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    sale_order_currency_id = fields.Many2one(
        string='Sale Order Currency',
        comodel_name='res.currency',
        compute='compute_sale_order_currency_id',
        store=True
    )
    price_per_unit = fields.Float(
        string='Price/Unit'
    )
    cost_per_unit = fields.Float(
        string='Cost/Unit'
    )
    price = fields.Float(
        string='Price',
        compute='compute_price'
    )
    cost = fields.Float(
        string='Cost',
        compute='compute_cost'
    )

    # ONCHANGES

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            local_currency = rec.product_id.currency_id
            local_price_per_unit = rec.product_id.lst_price
            local_cost_per_unit = rec.product_id.standard_price

            default_price_per_unit = self.to_sale_order_currency(
                local_currency, local_price_per_unit)
            default_cost_per_unit = self.to_sale_order_currency(
                local_currency, local_cost_per_unit)

            rec.price_per_unit = default_price_per_unit
            rec.cost_per_unit = default_cost_per_unit

    # COMPUTES

    @api.depends('bundle_details_id', 'bundle_details_id_epl')
    def compute_sale_order_currency_id(self):
        for rec in self:
            bd_id = rec.bundle_details_id or rec.bundle_details_id_epl
            rec.sale_order_currency_id = bd_id.sale_order_currency_id

    @api.depends('price_per_unit', 'quantity')
    def compute_price(self):
        for rec in self:
            rec.price = rec.price_per_unit * rec.quantity

    @api.depends('cost_per_unit', 'quantity')
    def compute_cost(self):
        for rec in self:
            rec.cost = rec.cost_per_unit * rec.quantity

    # TOOLS

    @api.model
    def to_sale_order_currency(self, from_currency, from_amount):
        return from_currency.sudo().compute(
            from_amount=from_amount,
            to_currency=self.sale_order_currency_id,
            round=False
        )
