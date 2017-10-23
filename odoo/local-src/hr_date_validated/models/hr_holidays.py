from odoo import models, fields, api
import datetime


class HrExpense(models.Model):
    _inherit = 'hr.holidays'

    date_validated = fields.Datetime()

    @api.multi
    def action_validate(self):
        res = super(HrExpense, self).action_validate()
        validated_at = datetime.datetime.now()
        for holiday in self:
            holiday.date_validated = validated_at
        return res

    @api.multi
    def action_refuse(self):
        res = super(HrExpense, self).action_refuse()
        for holiday in self:
            holiday.date_validated = False
        return res

    @api.multi
    def action_draft(self):
        res = super(HrExpense, self).action_draft()
        for holiday in self:
            holiday.date_validated = False
        return res
