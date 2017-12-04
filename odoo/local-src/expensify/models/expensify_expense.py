from odoo import models, fields, api


class ExpensifyExpense(models.TransientModel):
    _name = 'expensify.expense'
    _order = 'expensify_wizard_id ASC,' \
             'sequence ASC,' \
             'id ASC'

    expensify_wizard_id = fields.Many2one(
        comodel_name='expensify.wizard'
    )
    expensify_id = fields.Text(
        # ID too big for Integer type
    )
    sequence = fields.Integer(
        default=0
    )
    date = fields.Date(
        required=True
    )
    name = fields.Char(
        string='Description',
        required=True
    )
    amount = fields.Float(
        string='Amount',
        required=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    receipt = fields.Binary(
        string='Receipt'
        # Required in Wizard (validate_expensify_expenses)
    )
    description = fields.Text(
        string='Notes'
    )
    payment_mode = fields.Selection(
        string='Paid By',
        selection=[('own_account', 'Employee'),
                   ('company_account', 'Company')],
        default='own_account',
        required=True
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product'
        # Required in Wizard (validate_expensify_expenses)
    )
    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax'
        # Required in Wizard (validate_expensify_expenses)
    )
    analytic_account_id = fields.Many2one(
        string='Project',
        comodel_name='account.analytic.account'
    )

    @api.onchange('company_id')
    def onchange_company_id(self):
        for rec in self:
            rec.tax_id = False
