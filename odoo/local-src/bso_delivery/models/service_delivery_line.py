from odoo import fields, models, api


class DeliveryProjectLine(models.Model):
    _name = 'delivery.project.line'

    name = fields.Char(string='Name')

    delivery_id = fields.Many2one(
        string='Service delivery',
        comodel_name='delivery.project'
    )
    sale_order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='sale.order.line'
    )
    qty_delivered = fields.Float(
        related='sale_order_line_id.qty_delivered',
        read_only=True,
    )
    qty_invoiced = fields.Float(
        related='sale_order_line_id.qty_invoiced',
        read_only=True,
    )

    date_forecasted = fields.Date(
        string='Forecasted Date',
    )
    date_sla = fields.Date(
        string='SLA Date'
    )
    date_completed = fields.Date(
        string='Completed Date'
    )
    date_handover = fields.Date(
        string='Handover Date'
    )
    checked = fields.Boolean(
        string='Select'
    )