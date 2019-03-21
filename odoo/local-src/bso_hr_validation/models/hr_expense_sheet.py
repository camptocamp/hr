from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    validate_ok = fields.Boolean(
        string='Can Validate',
        compute='compute_validate_ok',
    )
    date_validated = fields.Datetime(
        string='Validated At',
    )
    date_refused = fields.Datetime(
        string='Refused At',
    )

    @api.multi
    def write(self, values):
        if 'state' in values:
            if values['state'] == 'submit':
                values['date_validated'] = False
                values['date_refused'] = False
            elif values['state'] == 'approve':
                values['date_validated'] = fields.Datetime.now()
            elif values['state'] == 'cancel':
                values['date_refused'] = fields.Datetime.now()
        return super(HrExpenseSheet, self).write(values)

    @api.depends('employee_id')
    def compute_validate_ok(self):
        for rec in self:
            self_validator = 'bso_hr_validation.group_self_validator'
            rec.validate_ok = (self.env.uid != rec.employee_id.user_id.id
                               or self.env.user.has_group(self_validator))

    @api.constrains('state')
    def check_validate_ok(self):
        for rec in self:
            if not rec.validate_ok:
                if rec.state == 'approve':
                    raise ValidationError(_("Cannot approve own expenses"))
                elif rec.state == 'cancel':
                    raise ValidationError(_("Cannot refuse own expenses"))
