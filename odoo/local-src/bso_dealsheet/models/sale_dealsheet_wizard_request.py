from odoo import models, fields, api


class SaleDealsheetWizardRequest(models.TransientModel):
    _name = 'sale.dealsheet.wizard.request'

    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        required=True
    )
    presale_id = fields.Many2one(
        string='Pre-Sale',
        comodel_name='res.users',
        domain=lambda self: [
            ('groups_id', 'in',
             self.env.ref('bso_dealsheet.group_dealsheet_role_presale').id)]
    )

    @api.multi
    def action_requested(self):
        dealsheet_id = self.env['sale.dealsheet'].sudo().create({
            'sale_order_id': self.sale_order_id.id
        })
        dealsheet_id.action_requested(self.presale_id)
        self.sale_order_id.update({
            'state': 'dealsheet',
            'dealsheet_id': dealsheet_id.id
        })
