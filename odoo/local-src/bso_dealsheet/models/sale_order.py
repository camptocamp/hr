from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('dealsheet', 'Dealsheet'),
        ]
    )

    @api.multi
    def dealsheet_action_request(self):
        return self.dealsheet_create().action_request()

    @api.multi
    def dealsheet_action_create(self):
        return self.dealsheet_create().action_create()

    @api.model
    def dealsheet_create(self):
        self.update({
            'state': 'dealsheet'
        })
        user_id = self.env.uid
        return self.env['sale.dealsheet'].sudo().create({
            'user_id': user_id,
            'sale_order_id': self.id
        })
