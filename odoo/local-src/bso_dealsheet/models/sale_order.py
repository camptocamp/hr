from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('dealsheet', 'Dealsheet'),
        ]
    )
    duration = fields.Integer(
        string='Duration (months)',
        default=12
    )

    @api.multi
    def action_dealsheet_request(self):
        dealsheet_id = self.env['sale.dealsheet'].create({
            'sale_order_id': self.id
        })

    @api.multi
    def action_dealsheet_create(self):
        dealsheet_id = self.env['sale.dealsheet'].create({
            'sale_order_id': self.id
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet",
            "res_id": dealsheet_id.id,
            "view_type": "form",
            "view_mode": "form",
        }
