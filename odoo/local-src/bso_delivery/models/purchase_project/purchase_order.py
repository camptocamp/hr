from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_project_id = fields.Many2one(
        string='Delivery Project',
        comodel_name='delivery.project.po',
    )

    amount_total_usd = fields.Monetary(
        string='Amount total USD',
        compute='compute_amount_total_usd',
        currency_field='usd_currency_id',
        stote=True
    )
    rate_usd = fields.Float(
        string='Rate USD',
        compute='_compute_rate_usd',
    )
    usd_currency_id = fields.Many2one(
        string='USD Currency',
        comodel_name='res.currency',
        default=lambda self: self.currency_id.browse(3),
        readonly=True,
    )

    @api.multi
    def _compute_rate_usd(self):
        for rec in self:
            if not all((rec.company_id, rec.currency_id,
                        rec.date_order)):
                continue
            if rec.currency_id.id == rec.usd_currency_id.id:
                rec.rate_usd = 1
            else:
                rec.rate_usd = rec.currency_id.with_context({
                    'company_id': rec.company_id.id,
                    'date': rec.date_order,
                })._get_conversion_rate(rec.currency_id, rec.usd_currency_id)

    @api.depends('amount_total', 'rate_usd')
    def compute_amount_total_usd(self):
        for rec in self:
            rec.amount_total_usd = rec.amount_total * rec.rate_usd

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for rec in self:
            if vals.get('delivery_project_id', False):
                rec.delivery_project_id.create_delivery_lines(
                    rec.delivery_project_id.order_ids.ids)
        return res
