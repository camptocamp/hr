from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cease_count = fields.Integer(
        string='Ceases',
        compute='compute_cease_count'
    )

    @api.multi
    def compute_cease_count(self):
        for rec in self:
            rec.cease_count = len(rec.get_cease_ids())

    @api.multi
    def action_get_ceases(self):
        self.ensure_one()
        action = self.env.ref(
            'bso_subscription_cease.action_view_cease').read()[0]
        action['domain'] = [('partner_id', '=', self.id)]
        return action

    @api.multi
    def get_cease_ids(self):
        self.ensure_one()
        return self.env['cease.order'].search(
            [('partner_id', '=', self.id)]).ids
