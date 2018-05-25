from odoo import models, fields, api, exceptions, _


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    employee_is_user = fields.Boolean(
        compute='compute_employee_is_user'
    )
    date_validated = fields.Datetime()
    date_refused = fields.Datetime()

    @api.depends('employee_id')
    def compute_employee_is_user(self):
        for rec in self:
            rec.employee_is_user = rec.employee_id.user_id.id == self.env.uid

    @api.multi
    def approve_expense_sheets(self):
        if any(rec.employee_is_user for rec in self):
            raise exceptions.ValidationError(_("Cannot approve own expenses"))
        res = super(HrExpenseSheet, self).approve_expense_sheets()
        validated_at = fields.Datetime.now()
        for rec in self:
            rec.date_validated = validated_at
        return res

    @api.multi
    def refuse_expenses(self, reason):
        if any(rec.employee_is_user for rec in self):
            raise exceptions.ValidationError(_("Cannot refuse own expenses"))
        res = super(HrExpenseSheet, self).refuse_expenses(reason)
        refused_at = fields.Datetime.now()
        for rec in self:
            rec.date_refused = refused_at
        return res

    @api.multi
    def reset_expense_sheets(self):
        res = super(HrExpenseSheet, self).reset_expense_sheets()
        for rec in self:
            rec.date_validated = False
            rec.date_refused = False
        return res
