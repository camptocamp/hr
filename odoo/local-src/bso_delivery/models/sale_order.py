from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_project_id = fields.Many2one(
        string='Delivey Project',
        comodel_name='delivery.project',
        readonly=True
    )

    @api.multi
    def create_project_delivery(self):
        for rec in self:
            delivery_project = rec.delivery_project_id.sudo().create({
                'name': '{} {}'.format(rec.name, rec.partner_id.name),
                'sale_order_id': rec.id,
                'date_signed': rec.confirmation_date
            })
            rec.sudo().update({'delivery_project_id': delivery_project.id})

    @api.multi
    def action_confirm(self):
        confirmed = super(SaleOrder, self).action_confirm()
        self.create_project_delivery()
        return confirmed
