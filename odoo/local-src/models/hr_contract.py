from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda self: self.employee_id.company_id
    )
    contract_raise_ids = fields.One2many(
        string='Raises',
        comodel_name='hr.contract.raise',
        inverse_name='contract_id',
        readonly=True
    )

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.company_id = self.employee_id.company_id.id

    @api.multi
    def write(self, vals):
        if 'wage' or 'wage_variable' in vals:
            values = {
                'wage_previous': self.wage,
                'wage_raise': vals['wage'] - self.wage if vals.get(
                    'wage') else 0,
                'wage_after': vals['wage'] if vals.get('wage') else self.wage,
                'bonus_previous': self.wage_variable,
                'bonus_raise': vals['wage_variable'] - self.wage_variable if
                vals.get('wage_variable') else 0,
                'bonus_after': vals['wage_variable'] if vals.get(
                    'wage_variable') else self.wage_variable,
                'contract_id': self.id
            }
            self.contract_raise_ids.create(values)
        return super(HrContract, self).write(vals)
