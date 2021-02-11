from odoo import models, fields, api


class DeliveryLineSo(models.Model):
    _name = 'delivery.line.so'
    _inherit = 'delivery.project.line'

    delivery_id = fields.Many2one(
        string='Sale Project',
        comodel_name='delivery.project.so'
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='sale.order.line'
    )
    product_id = fields.Many2one(
        related='order_line_id.product_id'
    )
    product_category = fields.Selection(
        related='document_id.so_product_category'
    )

    @api.model
    def create(self, vals):
        rec = super(DeliveryLineSo, self).create(vals)
        categ_id = rec.product_id.categ_id.id
        template_ids = rec.jira_product_template_ids.search([
            '&',
            ('category_id', '=', categ_id),
            ('template_type', '=', 'sale')])
        rec.write({
            'jira_product_template_ids': [(6, 0, template_ids)],
        })
        return rec
