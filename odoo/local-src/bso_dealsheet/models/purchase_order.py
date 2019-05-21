from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
    )
