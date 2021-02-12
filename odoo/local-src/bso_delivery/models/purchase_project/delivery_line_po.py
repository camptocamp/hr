from odoo import models, fields, api


class DeliveryLinePo(models.Model):
    _name = 'delivery.line.po'
    _inherit = 'delivery.project.line'

    delivery_id = fields.Many2one(
        string='Purchase Project',
        comodel_name='delivery.project.po'
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='purchase.order.line'
    )
    order_id = fields.Many2one(
        related='order_line_id.order_id',
        store=True
    )
    product_id = fields.Many2one(
        related='order_line_id.product_id',
        store=True
    )
    product_category = fields.Selection(
        related='document_id.po_product_category',
        store=True
    )

    @api.model
    def create(self, vals):
        rec = super(DeliveryLinePo, self).create(vals)
        categ_id = rec.product_id.categ_id.id
        template_ids = rec.jira_product_template_ids.search([
            '&',
            ('category_id', '=', categ_id),
            ('template_type', '=', 'purchase')])
        doc_id = rec.document_id.create({})
        rec.write({
            'jira_product_template_ids': [(6, 0, template_ids)],
            'document_id': doc_id.id
        })
        return rec
