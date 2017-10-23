from odoo import models, fields, api
import datetime


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    date_validated = fields.Datetime()

    @api.multi
    def approve_expense_sheets(self):
        res = super(HrExpenseSheet, self).approve_expense_sheets()
        validated_at = datetime.datetime.now()
        for sheet in self:
            sheet.date_validated = validated_at
        return res

    @api.multi
    def reset_expense_sheets(self):
        res = super(HrExpenseSheet, self).reset_expense_sheets()
        for sheet in self:
            sheet.date_validated = False
        return res

    @api.multi
    def refuse_expenses(self, reason):
        res = super(HrExpenseSheet, self).refuse_expenses(reason)
        for sheet in self:
            sheet.date_validated = False
        return res
