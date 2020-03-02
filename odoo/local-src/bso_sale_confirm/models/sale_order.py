from odoo import models, api, SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.env.uid == SUPERUSER_ID:
            return super(SaleOrder, self).action_confirm()
        if self.env.user.employee_ids.company_id != self.env.user.company_id:
            return self.env['pop.up.message'].show({
                'name': 'Confirm',
                'description': 'You are not on your home entity, Would you '
                               'like to to proceed with this action anyway?',
            })
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def _action_ok(self):
        return super(SaleOrder, self).action_confirm()
