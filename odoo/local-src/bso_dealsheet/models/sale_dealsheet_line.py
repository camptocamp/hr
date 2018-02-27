from odoo import models, fields


class SaleDealsheetLine(models.Model):
    _name = 'sale.dealsheet.line'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade'
    )
    is_cost = fields.Boolean(
        string='Is Cost'
    )
    is_recurring = fields.Boolean(
        string='Is Recurring'
    )
    currency_id = fields.Many2one(
        related='dealsheet_id.currency_id',
        readonly=True
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        domain=[('sale_ok', '=', True)],
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
    cost = fields.Float(
        string='Cost'
    )
    duration = fields.Integer(
        related='dealsheet_id.duration',
        readonly=True,
        store=False
    )
    sourcing_purchase_line_id = fields.Many2one(
        string='Sourcing purchase order line',
        comodel_name='purchase.order.line',
        readonly=True,
        ondelete='set null',
    )
