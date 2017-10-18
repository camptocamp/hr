from odoo import models, fields, api, exceptions, _
import datetime


class ExpensifyWizard(models.TransientModel):
    _name = 'expensify.wizard'

    employee_id = fields.Many2one(
        string='Employee ID',
        comodel_name='hr.employee',
        required=True
    )
    since_date = fields.Date(
        string='Since date',
        required=True
    )
    expensify_expenses = fields.One2many(
        string='Expenses',
        comodel_name='expensify.expense',
        inverse_name='expensify_wizard_id',
        required=True
    )

    @api.multi
    def button_import_submit(self):
        end_date = datetime.date.today()
        report_name = "Expensify (%s to %s)" % (self.since_date, end_date)
        expense_ids = self.create_expenses()

        report_id = self.env['hr.expense.sheet'].create({
            'name': report_name,
            'expense_line_ids': [(6, 0, expense_ids)]
        })

        # Show Report
        return {
            "name": report_name,
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.sheet",
            "res_id": report_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "self",
        }

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
        self.validate_expensify_expenses()
        expense_ids = []
        for expense in self.expensify_expenses:
            expense_data = {
                'expensify_id': expense.expensify_id,
                'name': expense.name,
                'date': expense.date,
                'employee_id': self.employee_id.id,
                'product_id': expense.product_id.id,
                'unit_amount': expense.amount,
                'tax_id': expense.tax_id.id,
                'company_id': expense.company_id.id,
                'currency_id': expense.currency_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'description': expense.description,
                'payment_mode': expense.payment_mode,
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
            expense_ids.append(expense_created.id)
        return expense_ids

    @api.model
    def validate_expensify_expenses(self):
        for expense in self.expensify_expenses:
            if not expense.receipt:
                raise exceptions.ValidationError(
                    _("Missing Receipt for Expense: %s" % expense.name)
                )
            if not expense.product_id:
                raise exceptions.ValidationError(
                    _("Missing Product for Expense: %s" % expense.name)
                )
            if not expense.tax_id:
                raise exceptions.ValidationError(
                    _("Missing Tax for Expense: %s" % expense.name)
                )
