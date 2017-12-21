from odoo import models, fields, api


class SaleDealsheetWizardConfirm(models.TransientModel):
    _name = 'sale.dealsheet.wizard.confirm'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade',
        required=True
    )
    reviewer_id = fields.Many2one(
        string='Reviewer',
        comodel_name='res.users'
    )

    @api.multi
    def action_confirmed(self):
        return self.dealsheet_id.action_confirmed(self.reviewer_id)
