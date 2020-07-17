from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_type = fields.Selection(
        related='order_id.order_type',
        store=True,
        readonly=True
    )
