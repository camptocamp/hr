from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('dealsheet', 'Dealsheet'),
        ]
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='pricelist_id.currency_id',
        required=False,
        readonly=True,
        store=True,
    )
    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        readonly=True,
        copy=False,
    )
    dealsheet_state = fields.Selection(
        string='Dealsheet Status',
        related='dealsheet_id.state',
        readonly=True
    )

    @api.multi
    def action_dealsheet(self):
        self.ensure_one()
        group_manager = 'bso_dealsheet.group_dealsheet_manager'
        if self.env.user.has_group(group_manager):
            return self.dealsheet_create().action_create()
        else:
            return self.env['sale.dealsheet'].action_request(self.id)

    @api.model
    def dealsheet_create(self):
        dealsheet_id = self.env['sale.dealsheet'].create({
            'sale_order_id': self.id
        })
        self.update({
            'dealsheet_id': dealsheet_id.id
        })
        return dealsheet_id
