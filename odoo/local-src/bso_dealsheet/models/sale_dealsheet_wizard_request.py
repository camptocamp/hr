from odoo import models, fields, api


class SaleDealsheetWizardRequest(models.TransientModel):
    _name = 'sale.dealsheet.wizard.request'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade',
        required=True
    )
    presale_id = fields.Many2one(
        string='Pre-Sale',
        comodel_name='res.users'
    )

    @api.multi
    def action_requested(self):
        return self.dealsheet_id.action_requested(self.presale_id)
