from odoo import models, fields, api


class SaleDealsheetWizard(models.TransientModel):
    _name = 'sale.dealsheet.wizard'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade',
        required=True
    )
    technical_reviewer_id = fields.Many2one(
        string='Technical Reviewer',
        comodel_name='res.users'
    )

    @api.multi
    def action_confirm(self):
        dealsheet_id = self.dealsheet_id.sudo()
        dealsheet_id.message_subscribe_users(self.technical_reviewer_id.id,
                                             [1, 2])
        dealsheet_id.update({
            'user_filled': self.env.uid,
            'state': 'confirmed'
        })
