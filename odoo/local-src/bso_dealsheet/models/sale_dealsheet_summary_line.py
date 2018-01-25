from odoo import models, fields, api


class SaleDealsheetSummaryLine(models.Model):
    _name = 'sale.dealsheet.summary.line'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade'
    )
    currency_id = fields.Many2one(
        related='dealsheet_id.currency_id',
        readonly=True
    )
    type = fields.Selection(
        string='',
        selection=[
            ('non_recurring', 'Non Recurring'),
            ('recurring', 'Recurring'),
            ('total', 'Total')
        ],
        required=True
    )
    cost = fields.Float(
        string='Cost',
        compute='compute_values',
        store=True
    )
    revenue = fields.Float(
        string='Revenue',
        compute='compute_values',
        store=True
    )
    margin = fields.Char(
        string='Margin',
        compute='compute_values',
        store=True
    )

    @api.depends('dealsheet_id.cost_upfront', 'dealsheet_id.price_upfront',
                 'dealsheet_id.margin_upfront', 'dealsheet_id.cost',
                 'dealsheet_id.price', 'dealsheet_id.margin',
                 'dealsheet_id.cost_total', 'dealsheet_id.price_total',
                 'dealsheet_id.margin_total', 'type')
    def compute_values(self):
        for rec in self:
            if rec.type == 'non_recurring':
                rec.update({
                    'cost': rec.dealsheet_id.cost_upfront,
                    'revenue': rec.dealsheet_id.price_upfront,
                    'margin': self.get_margin_str(
                        rec.dealsheet_id.margin_upfront)
                })
            elif rec.type == 'recurring':
                rec.update({
                    'cost': rec.dealsheet_id.cost,
                    'revenue': rec.dealsheet_id.price,
                    'margin': self.get_margin_str(rec.dealsheet_id.margin)
                })
            elif rec.type == 'total':
                rec.update({
                    'cost': rec.dealsheet_id.cost_total,
                    'revenue': rec.dealsheet_id.price_total,
                    'margin': self.get_margin_str(
                        rec.dealsheet_id.margin_total)
                })

    @api.model
    def get_margin_str(self, margin):
        return '%.2f %s' % (margin, '%')
