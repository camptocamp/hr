from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('dealsheet', 'Dealsheet'),
        ]
    )
    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        readonly=True
    )

    @api.multi
    def dealsheet_action_request(self):
        return self.dealsheet_create(sudo=True).action_request()

    @api.multi
    def dealsheet_action_create(self):
        return self.dealsheet_create(sudo=False).action_create()

    @api.model
    def dealsheet_create(self, sudo):
        dealsheet_model = self.env['sale.dealsheet']
        if sudo:
            dealsheet_model = dealsheet_model.sudo()
        dealsheet_id = dealsheet_model.create({
            'seller_id': self.env.uid,
            'sale_order_id': self.id,
        })
        self.update({
            'state': 'dealsheet',
            'dealsheet_id': dealsheet_id.id,
        })
        return dealsheet_id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'dealsheet':
                rec.write({'state': 'draft'})
        return super(SaleOrder, self).unlink()
