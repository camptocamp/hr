from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    expensify_api_id = fields.Char(
        string='partnerUserID'
    )
    expensify_api_secret = fields.Char(
        string='partnerUserSecret'
    )
    expensify_convert_currency = fields.Boolean(
        string='Convert currency',
        default=True
    )
    expensify_deduct_surcharge = fields.Boolean(
        string='Deduct surcharge',
        default=True
    )
