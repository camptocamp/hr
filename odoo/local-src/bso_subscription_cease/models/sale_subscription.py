from odoo import models, api, fields


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    cease_count = fields.Integer(
        string='Cease Count',
        compute='compute_cease_count'
    )

    @api.multi
    def compute_cease_count(self):
        for rec in self:
            rec.cease_count = len(self.env['cease.order'].search(
                [('subscription_id', '=', rec.id)]))

    @api.multi
    def action_cease_lines(self):
        self.ensure_one()
        wizard = self.env['replace.subscription.lines.wizard'].create(
            {'subscription_id': self.id})
        return {
            'name': 'Cease Options',
            'type': 'ir.actions.act_window',
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_id': self.env.ref(
                'bso_subscription_cease.cease_subscription_lines_wizard'
            ).id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.multi
    def action_get_ceases(self):
        self.ensure_one()
        action = self.env.ref(
            'bso_subscription_cease.action_view_cease').read()[0]
        action['domain'] = [('subscription_id', '=', self.id)]
        return action
