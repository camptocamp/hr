from odoo import models, fields


class ExpensifyConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'expensify.config.settings'

    default_api_url = fields.Char(
        string='Url',
        default_model='expensify'
    )
    default_api_report_states = fields.Char(
        string='Report states',
        default_model='expensify'
    )
    default_convert_currency = fields.Boolean(
        string='Convert currency',
        default_model='expensify'
    )
    default_deduct_surcharge = fields.Boolean(
        string='Deduct surcharge',
        default_model='expensify'
    )
