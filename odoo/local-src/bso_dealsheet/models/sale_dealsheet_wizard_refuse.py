from odoo import models, fields, api


class SaleDealsheetWizardRefuse(models.TransientModel):
    _name = 'sale.dealsheet.wizard.refuse'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade',
        required=True
    )
    reason = fields.Text(
        string='Reason'
    )

    @api.multi
    def action_refused(self):
        return self.dealsheet_id.action_refused(self.reason)
