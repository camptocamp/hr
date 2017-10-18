from odoo import models, fields


class ExpensifyCategory(models.Model):
    _name = 'expensify.category'

    name = fields.Char(
        string='Category',
        required=True
    )
