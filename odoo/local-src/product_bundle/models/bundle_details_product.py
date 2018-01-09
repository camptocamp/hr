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
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        compute='compute_currency_id'
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
        related='product_id.uom_id',
        readonly=True
    )
    cost_upfront = fields.Float(
        string='Non Recurring Cost'
    )
    cost_per_unit = fields.Float(
        string='Recurring Cost / Unit',
        required=True
    )
    cost = fields.Float(
        string='Recurring Cost',
        compute='compute_cost'
    )
    price_upfront = fields.Float(
        string='Non Recurring Price'
    )
    price_per_unit = fields.Float(
        string='Recurring Price / Unit',
        required=True
    )
    price = fields.Float(
        string='Recurring Price',
        compute='compute_price'
    )

    # ONCHANGES

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            local_currency = rec.product_id.currency_id
            local_cost_per_unit = rec.product_id.standard_price
            local_price_per_unit = rec.product_id.lst_price

            default_cost_per_unit = local_currency.sudo().compute(
                from_amount=local_cost_per_unit,
                to_currency=rec.currency_id,
                round=False
            )
            default_price_per_unit = local_currency.sudo().compute(
                from_amount=local_price_per_unit,
                to_currency=rec.currency_id,
                round=False
            )

            rec.update({
                'cost_per_unit': default_cost_per_unit,
                'price_per_unit': default_price_per_unit,
            })

    # COMPUTES

    @api.depends('bundle_details_id.currency_id',
                 'bundle_details_id_epl.currency_id')
    def compute_currency_id(self):
        for rec in self:
            currency_id = rec.bundle_details_id.currency_id \
                          or rec.bundle_details_id_epl.currency_id
            rec.update({
                'currency_id': currency_id
            })

    @api.depends('cost_per_unit', 'quantity', 'currency_id')
    def compute_cost(self):
        for rec in self:
            rec.update({
                'cost': rec.cost_per_unit * rec.quantity
            })

    @api.depends('price_per_unit', 'quantity', 'currency_id')
    def compute_price(self):
        for rec in self:
            rec.update({
                'price': rec.price_per_unit * rec.quantity
            })
