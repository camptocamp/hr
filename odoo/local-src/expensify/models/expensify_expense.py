from odoo import models, fields


class ExpensifyExpense(models.TransientModel):
    _name = 'expensify.expense'
    _order = 'expensify_wizard_id ASC,' \
             'sequence ASC,' \
             'id ASC'

    sequence = fields.Integer(
        default=0
    )
    expensify_wizard_id = fields.Many2one(
        comodel_name='expensify.wizard'
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
