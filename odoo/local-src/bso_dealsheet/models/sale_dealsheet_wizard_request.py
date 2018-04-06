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
        string='Presale',
        comodel_name='res.users',
        domain=lambda self: [
            ('groups_id', 'in',
             self.env.ref('bso_dealsheet.group_dealsheet_role_presale').id)]
    )

    @api.multi
    def action_requested(self):
        return self.dealsheet_id.sudo().action_requested(self.presale_id)
