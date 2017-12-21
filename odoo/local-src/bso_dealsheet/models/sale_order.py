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
    def dealsheet_action_request(self):
        return self.dealsheet_create().action_request()

    @api.multi
    def dealsheet_action_create(self):
        return self.dealsheet_create().action_create()

    @api.model
    def dealsheet_create(self):
        return self.env['sale.dealsheet'].sudo().create({
            'sale_order_id': self.id
        })
