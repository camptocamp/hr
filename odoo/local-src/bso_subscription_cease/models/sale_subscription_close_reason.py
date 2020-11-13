from odoo import models, fields


class SaleSubscriptionCloseReason(models.Model):
    _inherit = 'sale.subscription.close.reason'

    is_revenue_loss = fields.Boolean(
        string='Revenue Loss',
        default=True
    )
