from odoo import models, fields


class SaleDealsheet(models.Model):
    _inherit = 'sale.dealsheet'

    purchase_order = fields.One2many(
        comodel_name='purchase.order',
        string='purchase order',
        inverse_name='id'
    )
