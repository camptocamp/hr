from openerp import models, fields, api


class ExpensifyWizard(models.TransientModel):
    _name = 'expensify.wizard'

    employee_id = fields.Many2one(
        string='Employee ID',
        comodel_name='hr.employee',
        required=True
    )
    expensify_expenses = fields.One2many(
        string='Expenses',
        comodel_name='expensify.expense',
        inverse_name='expensify_wizard_id',
        required=True
    )

    @api.multi
    def button_import(self):
        for expense in self.expensify_expenses:
            expense_data = {
                'expensify_id': expense.expensify_id,
                'date': expense.date,
                'name': expense.name,
                'product_id': expense.product_id.id,
                'quantity': 1,
                'unit_amount': expense.amount,
                'tax_ids': [[6, False, [tax.id for tax in expense.tax_ids]]],
                'currency_id': expense.currency_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'payment_mode': expense.payment_mode,
                'description': expense.description,
                'company_id': expense.company_id.id,
                'employee_id': self.employee_id.id
            }
            expense_created = self.env['hr.expense'].create(expense_data)

            if expense.receipt:
                attachment_data = {
                    'res_id': expense_created.id,
                    'res_model': 'hr.expense',
                    'company_id': expense.company_id.id,
                    'name': 'Receipt',
                    'type': 'binary',
                    'datas_fname': 'receipt_%s.jpg' % expense_created.id,
                    'datas': expense.receipt
                }
                self.env['ir.attachment'].create(attachment_data)

        # Show unsubmitted expenses
        return self.env['ir.actions.act_window'].for_xml_id(
            module='hr_expense',
            xml_id='hr_expense_actions_my_unsubmitted'
        )
