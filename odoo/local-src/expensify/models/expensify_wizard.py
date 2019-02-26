from odoo import models, fields, api


class ExpensifyWizard(models.TransientModel):
    _name = 'expensify.wizard'

    employee_id = fields.Many2one(
        string='Employee',
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
        self.create_expenses()

        # Show unsubmitted expenses
        return self.env['ir.actions.act_window'].for_xml_id(
            module='hr_expense',
            xml_id='hr_expense_actions_my_unsubmitted'
        )

    # TOOLS

    @api.model
    def create_expenses(self):
        expense_ids = []
        for expense in self.expensify_expenses:
            expense_data = {
                'expensify_id': expense.expensify_id,
                'name': expense.name,
                'date': expense.date,
                'employee_id': self.employee_id.id,
                'product_id': expense.product_id.id,
                'company_id': self.employee_id.company_id.id,
                'currency_id': expense.currency_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'description': expense.description,
                'unit_amount': 0,  # Set after onchange_product_id()
            }
            expense_created = self.env['hr.expense'].create(expense_data)
            expense_created._onchange_product_id()
            expense_created.unit_amount = expense.amount
            if expense.receipt:
                attachment_data = {
                    'res_id': expense_created.id,
                    'res_model': 'hr.expense',
                    'company_id': self.employee_id.company_id.id,
                    'name': 'Receipt',
                    'type': 'binary',
                    'datas_fname': 'receipt_%s' % expense_created.id,
                    'datas': expense.receipt
                }
                self.env['ir.attachment'].create(attachment_data)
            expense_ids.append(expense_created.id)
        return expense_ids
