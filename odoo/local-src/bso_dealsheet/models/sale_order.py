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
        model_dealsheet = self.env['sale.dealsheet']
        group_manager = 'bso_dealsheet.group_dealsheet_manager'
        if self.env.user.has_group(group_manager):
            dealsheet_id = model_dealsheet.create({})
            self.update({
                'state': 'dealsheet',
                'dealsheet_id': dealsheet_id.id
            })
            return dealsheet_id.action_create()
        else:
            return model_dealsheet.action_request()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'dealsheet':
                rec.write({'state': 'draft'})
        return super(SaleOrder, self).unlink()
