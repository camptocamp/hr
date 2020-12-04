from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        return super(
            AccountInvoice, self.with_context(tracking_disable=True)
        ).create(vals)
