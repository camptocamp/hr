from odoo import models, fields, api


class ExpensifyExpense(models.TransientModel):
    _name = 'expensify.expense'

    expensify_wizard_id = fields.Many2one(
        comodel_name='expensify.wizard',
        required=True
    )
    expensify_id = fields.Text(  # ID too big for Integer type
        required=True
    )
    date = fields.Date(
        required=True
    )
    name = fields.Char(
        string='Description',
        required=True
    )
    amount = fields.Float(
        required=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    receipt = fields.Binary(
        string='Receipt'
        # Requirement validation in Wizard
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
    expensify_category_id = fields.Many2one(
        string='Category',
        comodel_name='expensify.category'
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product'
        # Requirement validation in Wizard
    )
    analytic_account_id = fields.Many2one(
        string='Project',
        comodel_name='account.analytic.account'
    )

    @api.onchange('company_id')
    def onchange_company_id(self):
        for rec in self:
            rec.product_id = False
