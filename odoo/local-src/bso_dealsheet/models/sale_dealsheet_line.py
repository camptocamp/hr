from odoo import models, fields


class SaleDealsheetLine(models.Model):
    _name = 'sale.dealsheet.line'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade'
    )
    dealsheet_state = fields.Selection(
        related='dealsheet_id.state',
        track_visibility=False,
        store=True
    )
    is_cost = fields.Boolean(
        string='Is Cost'
    )
    is_recurring = fields.Boolean(
        string='Is Recurring'
    )
    currency_id = fields.Many2one(
        related='dealsheet_id.currency_id',
        readonly=True,
        store=True
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        domain=['|', ('sale_ok', '=', True), ('purchase_ok', '=', True)],
        required=True
    )
    product_categ_id = fields.Many2one(
        string='Product Category',
        related='product_id.categ_id',
        readonly=True,
        store=True
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
        readonly=True,
        store=True
    )
    cost = fields.Monetary(
        string='Cost'
    )
    cost_delivery = fields.Monetary(
        string='Delivery Cost'
    )
