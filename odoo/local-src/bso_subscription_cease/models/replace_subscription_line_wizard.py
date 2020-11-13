from odoo import models, fields, api


class ReplaceSubsriptionLinesWizard(models.TransientModel):
    _inherit = 'replace.subscription.lines.wizard'

    close_reason_id = fields.Many2one(
        string='Close Reason',
        comodel_name='sale.subscription.close.reason')
    reason_description = fields.Text(
        string='Reason Description'
    )

    @api.multi
    def cease_action(self):
        self.ensure_one()
        cease_lines = []
        for line in self.subscription_line_ids:
            cease_lines.append(self.env['cease.order.line'].create(
                {'subscription_line_id': line.id}).id)

        cease_id = self.env['cease.order'].create({
            'subscription_id': self.subscription_id.id,
            'close_reason_id': self.close_reason_id.id,
            'reason_description': self.reason_description,
            'cease_line_ids': [(6, 0, cease_lines)]
        })
        cease_id.write({'name': '{0}{1:05d}'.format('CO', cease_id.id)})

        if len(self.subscription_id.recurring_invoice_line_ids) == len(
                self.subscription_line_ids):
            cease_id.cease_type = 'full'

        return {
            'name': 'Cease %s' % str(cease_id),
            'type': 'ir.actions.act_window',
            'res_model': cease_id._name,
            'res_id': cease_id.id,
            'view_type': 'form',
            'view_mode': 'form',
        }
