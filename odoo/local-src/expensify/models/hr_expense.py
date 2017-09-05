from odoo import models, fields


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    expensify_id = fields.Text()  # ID too big for Integer type
