from odoo import models, fields


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    unlink_order_id = fields.Many2one(
        string='Order to unlink from',
        comodel_name='sale.order'
    )
