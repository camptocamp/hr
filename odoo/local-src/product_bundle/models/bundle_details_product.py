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
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True
    )
    name = fields.Char(
        string='Name',
        related='product_id.display_name',
        readonly=True
    )
    uom_id = fields.Many2one(
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    local_currency_id = fields.Many2one(
        string='Local Currency',
        related='product_id.currency_id',
        readonly=True
    )
    local_price_per_unit = fields.Float(
        string='Local Price/Unit',
        related='product_id.lst_price',
        readonly=True
    )
    local_cost_per_unit = fields.Float(
        string='Local Cost/Unit',
        related='product_id.standard_price',
        readonly=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    price_per_unit = fields.Monetary(
        string='Price/Unit',
        currency_field='currency_id',
        compute='compute_price_per_unit'
    )
    cost_per_unit = fields.Monetary(
        string='Cost/Unit',
        currency_field='currency_id',
        compute='compute_price_per_unit'
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        compute='compute_price',
    )
    cost = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        compute='compute_cost',
    )

    @api.depends('product_id', 'currency_id')
    def compute_price_per_unit(self):
        for rec in self:
            rec.price_per_unit = rec.local_currency_id.sudo().compute(
                from_amount=rec.local_price_per_unit,
                to_currency=rec.currency_id
            )

    @api.depends('product_id', 'currency_id')
    def compute_cost_per_unit(self):
        for rec in self:
            rec.cost_per_unit = rec.local_currency_id.sudo().compute(
                from_amount=rec.local_cost_per_unit,
                to_currency=rec.currency_id
            )

    @api.depends('price_per_unit', 'quantity')
    def compute_price(self):
        for rec in self:
            rec.price = rec.price_per_unit * rec.quantity

    @api.depends('cost_per_unit', 'quantity')
    def compute_cost(self):
        for rec in self:
            rec.cost = rec.cost_per_unit * rec.quantity
