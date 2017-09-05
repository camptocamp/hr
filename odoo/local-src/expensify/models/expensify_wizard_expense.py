from openerp import models, fields, api, exceptions, _


class ExpensifyWizardExpense(models.TransientModel):
    _name = 'expensify.wizard.expense'

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
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
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
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True
    )
    tax_ids = fields.Many2many(
        string='Taxes',
        comodel_name='account.tax',
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
