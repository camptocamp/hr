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
    def action_dealsheet(self):
        group_manager = 'bso_dealsheet.group_dealsheet_manager'
        if self.env.user.has_group(group_manager):
            return self.dealsheet_create()
        else:
            return self.dealsheet_request()

    @api.model
    def dealsheet_create(self):
        dealsheet_id = self.env['sale.dealsheet'].create({
            'sale_order_id': self.id
        })
        self.update({
            'state': 'dealsheet',
            'dealsheet_id': dealsheet_id.id
        })
        return dealsheet_id.action_create()

    @api.model
    def dealsheet_request(self):
        return self.env['sale.dealsheet'].action_request(self.id)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'dealsheet':
                rec.write({'state': 'draft'})
        return super(SaleOrder, self).unlink()
