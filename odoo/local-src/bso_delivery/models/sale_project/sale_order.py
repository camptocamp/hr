from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_id = fields.Many2one(
        string='Delivey Project',
        comodel_name='delivery.project.so',
        readonly=True,
        oldname='delivery_project_id'
    )

    @api.multi
    def create_project_delivery(self):
        for rec in self:
            delivery_project = rec.delivery_id.sudo().create({
                'name': '{} {}'.format(rec.name, rec.partner_id.name),
                'order_id': rec.id,
            })
            rec.sudo().update({'delivery_id': delivery_project.id})

    def update_project_delivery(self):
        for rec in self:
            rec.delivery_id.delivery_line_ids.unlink()
            rec.delivery_id.get_delivery_lines()

    @api.multi
    def action_confirm(self):
        confirmed = super(SaleOrder, self).action_confirm()
        if not self.delivery_id:
            self.create_project_delivery()
        else:
            self.delivery_id.sudo().state = 'kickoff'
        return confirmed

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec.delivery_id:
                if vals.get('state') in ('cancel', 'draft'):
                    rec.delivery_id.sudo().state = 'cancel'
                for dm in vals.get('order_line', []):
                    if dm[0] == 2:
                        dl_id = self.env['delivery.line.so'].search(
                            [('order_line_id', '=', dm[1])])
                        rec.delivery_id.sudo().write(
                            {'delivery_line_ids': [[2, dl_id.id]]})
        return super(SaleOrder, self).write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        rec = super(SaleOrderLine, self).create(vals)
        if rec.order_id.delivery_id:
            self.env['delivery.line.so'].create({
                'name': rec.name,
                'delivery_id': rec.order_id.delivery_id.id,
                'order_line_id': rec.id
            })
        return rec
