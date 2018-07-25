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
        readonly=True,
        store=True
    )
    cost_type = fields.Selection(
        selection=[
            ('nr', 'Non Recurring'),
            ('mr', 'Recurring'),
            ('total', 'Total')
        ],
        required=True
    )
    cost = fields.Float(
        string='Cost',
        compute='compute_values',
        store=True
    )
    cost_delivery = fields.Float(
        string='Delivery Cost',
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
    margin_delivery = fields.Char(
        string='Delivery Margin',
        compute='compute_values',
        store=True
    )

    @api.depends('dealsheet_id.nrc', 'dealsheet_id.nrc_delivery',
                 'dealsheet_id.nrr', 'dealsheet_id.nrm',
                 'dealsheet_id.nrm_delivery', 'dealsheet_id.mrc',
                 'dealsheet_id.mrc_delivery', 'dealsheet_id.mrr',
                 'dealsheet_id.mrm', 'dealsheet_id.mrm_delivery',
                 'dealsheet_id.cost', 'dealsheet_id.cost_delivery',
                 'dealsheet_id.revenue', 'dealsheet_id.margin',
                 'dealsheet_id.margin_delivery', 'cost_type')
    def compute_values(self):
        for rec in self:
            if rec.cost_type == 'nr':
                rec.update(self._data(rec.dealsheet_id.nrc,
                                      rec.dealsheet_id.nrc_delivery,
                                      rec.dealsheet_id.nrr,
                                      rec.dealsheet_id.nrm,
                                      rec.dealsheet_id.nrm_delivery))
            elif rec.cost_type == 'mr':
                rec.update(self._data(rec.dealsheet_id.mrc,
                                      rec.dealsheet_id.mrc_delivery,
                                      rec.dealsheet_id.mrr,
                                      rec.dealsheet_id.mrm,
                                      rec.dealsheet_id.mrm_delivery))
            elif rec.cost_type == 'total':
                rec.update(self._data(rec.dealsheet_id.cost,
                                      rec.dealsheet_id.cost_delivery,
                                      rec.dealsheet_id.revenue,
                                      rec.dealsheet_id.margin,
                                      rec.dealsheet_id.margin_delivery))

    @api.model
    def _data(self, cost, cost_delivery, revenue, margin, margin_delivery):
        return {'cost': cost,
                'cost_delivery': cost_delivery,
                'revenue': revenue,
                'margin': self.get_margin_str(margin),
                'margin_delivery': self.get_margin_str(margin_delivery)}

    @api.model
    def get_margin_str(self, margin):
        return '%.2f %%' % margin
