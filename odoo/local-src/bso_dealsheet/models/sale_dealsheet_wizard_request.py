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
        self.env['sale.dealsheet'].action_requested(self.sale_order_id,
                                                    self.presale_id)
