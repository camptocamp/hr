from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ExpensifyExpense(models.TransientModel):
    _name = 'expensify.expense'
    _order = 'expensify_wizard_id ASC,' \
             'sequence ASC,' \
             'id ASC'

    sequence = fields.Integer(
        default=0,
    )
    expensify_wizard_id = fields.Many2one(
        comodel_name='expensify.wizard',
    )
    expensify_id = fields.Text(
        # ID too big for Integer type
    )
    date = fields.Date(
        string='Date',
    )
    name = fields.Char(
        string='Description',
    )
    amount = fields.Float(
        string='Amount',
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
    )
    receipt = fields.Binary(
        string='Receipt',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    analytic_account_id = fields.Many2one(
        string='Project',
        comodel_name='account.analytic.account'
    )
    description = fields.Text(
        string='Notes'
    )

    @api.multi
    def validate(self):
        for idx, rec in enumerate(self):
            if not rec.date:
                return rec.raise_invalid(idx, "date")
            if not rec.name:
                return rec.raise_invalid(idx, "description")
            if not rec.amount:
                return rec.raise_invalid(idx, "amount")
            if not rec.currency_id:
                return rec.raise_invalid(idx, "currency")
            if not rec.receipt:
                return rec.raise_invalid(idx, "receipt")
            if not rec.product_id:
                return rec.raise_invalid(idx, "product")

    def raise_invalid(self, idx, field):
        raise ValidationError(_("Missing %s for expense '%s' on %s (index %s)"
                                % (field, self.name, self.date, idx)))
