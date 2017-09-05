from openerp import models, fields, api


class ExpensifyWizard(models.TransientModel):
    _name = 'expensify.wizard'

    employee_id = fields.Many2one(
        string='Employee ID',
        comodel_name='hr.employee',
        required=True
    )
    expenses = fields.One2many(
        comodel_name='expensify.wizard.expense',
        inverse_name='expensify_wizard_id',
        required=True
    )

    @api.onchange('employee_id')
    def load_expenses(self):
        for rec in self:
            if not rec.employee_id:
                continue
            rec.expenses = [(0, 0, expense) for expense in
                            self.env.context.get('expensify_expenses', [])]

    @api.multi
    def button_import(self):
        for expense in self.expenses:
            expense_data = {
                'expensify_id': expense.expensify_id,
                'date': expense.date,
                'name': expense.name,
                'product_id': expense.product_id.id,
                'quantity': 1,
                'unit_amount': expense.amount,
                'tax_ids': [
                    [6, False, [tax_id.id for tax_id in expense.tax_ids]]],
                'currency_id': expense.currency_id.id,
                'payment_mode': expense.payment_mode,
                'description': expense.description,
                'company_id': expense.company_id.id,
                'employee_id': self.employee_id.id
            }
            imported = self.env['hr.expense'].create(expense_data)

            if expense.receipt:
                attachment_data = {
                    'res_id': imported.id,
                    'res_model': 'hr.expense',
                    'company_id': expense.company_id.id,
                    'name': 'Receipt',
                    'type': 'binary',
                    'datas_fname': 'receipt_%s.jpg' % imported.id,
                    'datas': expense.receipt
                }
                attached = self.env['ir.attachment'].create(attachment_data)
