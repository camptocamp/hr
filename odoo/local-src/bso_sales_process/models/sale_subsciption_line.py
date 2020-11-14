from odoo import models, fields


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    unlink_order_id = fields.Many2one(
        string='Unlink sale order',
        comodel_name='sale.order'
    )
