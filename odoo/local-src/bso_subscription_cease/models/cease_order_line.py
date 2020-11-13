from odoo import models, fields


class CeaseOrderLine(models.Model):
    _name = 'cease.order.line'
    # _inherits = {'sale.subscription.line': 'subscription_line_id'}

    cease_id = fields.Many2one(
        string='Cease Order',
        comodel_name='cease.order'
    )
    subscription_line_id = fields.Many2one(
        string='Subscription Line',
        comodel_name='sale.subscription.line',
    )
    name = fields.Text(
        related='subscription_line_id.name',
        store=True
    )
    product_id = fields.Many2one(
        related='subscription_line_id.product_id',
        store=True
    )
    quantity = fields.Float(
        related='subscription_line_id.quantity',
        store=True
    )
    sold_quantity = fields.Float(
        related='subscription_line_id.sold_quantity',
        store=True
    )
    uom_id = fields.Many2one(
        related='subscription_line_id.uom_id',
        store=True
    )
    price_unit = fields.Float(
        related='subscription_line_id.price_unit',
        store=True
    )
    discount = fields.Float(
        related='subscription_line_id.discount',
        store=True
    )
    price_subtotal = fields.Float(
        related='subscription_line_id.price_subtotal',
        store=True
    )
