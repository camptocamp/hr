# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_nrc = fields.Monetary(
        compute='_split_total_into_nrc_mrc',
        string='Total NRC',
        readonly=True)

    amount_mrc = fields.Monetary(
        compute='_split_total_into_nrc_mrc',
        string='Total MRC',
        readonly=True)
    product_category_id = fields.Many2one(
        string='Product category',
        comodel_name='product.category',
    )
    estimated_delivery_date = fields.Integer(
        string="Estimated delivery date",
    )

    @api.depends('order_line.price_subtotal')
    def _split_total_into_nrc_mrc(self):
        for rec in self:
            rec.update({
                'amount_mrc':
                    sum(l.price_subtotal for l in rec.order_line if
                        l.product_id.product_tmpl_id.recurring_invoice),
                'amount_nrc':
                    sum(l.price_subtotal for l in rec.order_line if
                        not l.product_id.product_tmpl_id.recurring_invoice)
            })
