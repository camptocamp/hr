from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    can_be_expensed = fields.Boolean(
        string='Can be Expensed',
        default=False
    )
