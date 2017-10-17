from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    tax_ids = fields.Many2many(
        string='Taxes',
        comodel_name='account.tax',
        relation='expense_tax',
        column1='expense_id',
        column2='tax_id',
        compute='compute_tax_ids',
        store=True
    )

    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax',
        states={'done': [('readonly', True)], 'post': [('readonly', True)]},
        required=True
    )

    @api.depends('tax_id')
    def compute_tax_ids(self):
        for rec in self:
            if rec.tax_id:
                rec.tax_ids = [(6, 0, [rec.tax_id.id])]
