from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    dealsheet_line_id = fields.Many2one(
        string='Dealsheet Line',
        comodel_name='sale.dealsheet.line',
    )
