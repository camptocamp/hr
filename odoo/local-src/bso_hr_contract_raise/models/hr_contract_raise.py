from odoo import models, fields


class HrContractRaise(models.Model):
    _name = 'hr.contract.raise'

    contract_id = fields.Many2one(
        string='Contract',
        comodel_name='hr.contract'
    )
    date = fields.Date(
        string='Raise Date',
        default=fields.Date.today()
    )
    wage_previous = fields.Float(
        string='Wage Previous',
    )
    wage_raise = fields.Float(
        string='Wage Raise',
    )
    wage_after = fields.Float(
        string='Wage After',
    )
    bonus_previous = fields.Float(
        string='Bonus Previous',
    )
    bonus_raise = fields.Float(
        string='Bonus Raise',
    )
    bonus_after = fields.Float(
        string='Bonus After',
    )
