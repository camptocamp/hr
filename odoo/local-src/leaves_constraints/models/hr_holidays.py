from odoo import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    employee_is_user = fields.Boolean(
        compute='compute_employee_is_user'
    )

    @api.depends('employee_id')
    def compute_employee_is_user(self):
        for rec in self:
            rec.employee_is_user = rec.employee_id.user_id.id == self.env.uid
