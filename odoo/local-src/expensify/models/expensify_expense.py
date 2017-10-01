from odoo import models, fields, api


class ExpensifyWizardExpense(models.TransientModel):
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
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True
    )
    analytic_account_id = fields.Many2one(
        string='Project',
        comodel_name='account.analytic.account'
    )
    name = fields.Char(
        string='Description',
        required=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    amount = fields.Float(
        required=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    payment_mode = fields.Selection(
        string='Paid By',
        selection=[('own_account', 'Employee'),
                   ('company_account', 'Company')],
        default='own_account',
        required=True
    )
    description = fields.Text(
        string='Notes'
    )
    receipt = fields.Binary()

    @api.onchange('company_id')
    def onchange_company_id(self):
        for rec in self:
            rec.product_id = False
