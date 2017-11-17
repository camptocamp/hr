from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    employee_is_user = fields.Boolean(
        compute='compute_employee_is_user'
    )
    date_validated = fields.Datetime()

    @api.depends('employee_id')
    def compute_employee_is_user(self):
        for rec in self:
            rec.employee_is_user = rec.employee_id.user_id.id == self.env.uid

    @api.multi
    def action_validate(self):
        for rec in self:
            if rec.employee_is_user:
                raise ValidationError(_("Cannot approve own leave"))
        res = super(HrHolidays, self).action_validate()
        validated_at = fields.Datetime.now()
        for rec in self:
            rec.date_validated = validated_at
        return res

    @api.multi
    def action_refuse(self):
        for rec in self:
            if rec.employee_is_user:
                raise ValidationError(_("Cannot refuse own leave"))
        res = super(HrHolidays, self).action_refuse()
        for rec in self:
            rec.date_validated = False
        return res

    @api.multi
    def action_draft(self):
        res = super(HrHolidays, self).action_draft()
        for rec in self:
            rec.date_validated = False
        return res
