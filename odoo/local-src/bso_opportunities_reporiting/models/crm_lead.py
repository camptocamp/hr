from odoo import models, fields, api


class CrmLeads(models.Model):
    _inherit = 'crm.lead'

    order_type = fields.Selection(
        string='Order Type',
        selection=[
            ('create', 'New Project'),
            ('upsell', 'Upsell'),
            ('replace', 'Replacement'),
            ('renew', 'Renewal'),
            ('cancel', 'Cancellation')
        ],
    )
    product_category_id = fields.Many2one(
        string='Product Category',
        comodel_name='product.category'
    )
    planned_revenue_new_mrc = fields.Monetary(
        string='New MRC',
        currency_field='currency_id',
    )
    planned_revenue_renew_mrc = fields.Monetary(
        string='Renew MRC',
        compute='_compute_renew_mrr',
        currency_field='currency_id',
        store=True,
    )
    new_planned_revenue = fields.Monetary(
        string='New TCV',
        compute='_compute_new_planned_revenue',
        currency_field='currency_id',
    )
    new_weighted_revenue = fields.Monetary(
        string='New Adjusted TCV',
        compute='_compute_new_wieghted_revenue',
        currency_field='currency_id',
    )
    planned_revenue_new_mrc_usd = fields.Monetary(
        string='New MRC',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )
    planned_revenue_renew_mrc_usd = fields.Monetary(
        string='Renew MRC',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
        store=True,
    )
    new_planned_revenue_usd = fields.Monetary(
        string='New TCV',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )
    new_weighted_revenue_usd = fields.Monetary(
        string='New Adjusted TCV',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )

    planned_revenue_new_mrc_eur = fields.Monetary(
        string='New MRC',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )
    planned_revenue_renew_mrc_eur = fields.Monetary(
        string='Renew MRC',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
        store=True,
    )
    new_planned_revenue_eur = fields.Monetary(
        string='New TCV',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )
    new_weighted_revenue_eur = fields.Monetary(
        string='New Adjusted TCV',
        compute='_compute_new_planned_revenue_currency',
        currency_field='currency_id',
    )

    display_planned_revenue_new_mrc = fields.Monetary(
        string='New MRC',
        currency_field='currency_id',
        compute='_compute_display_planned_new_revenues'
    )
    display_planned_revenue_renew_mrc = fields.Monetary(
        string='Renew MRC',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_id',
        store=True,
    )
    display_new_planned_revenue = fields.Monetary(
        string='New TCV',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_id',
    )
    display_new_weighted_revenue = fields.Monetary(
        string='New Adjusted TCV',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_id',
    )

    @api.multi
    @api.depends('planned_revenue_new_mrc', 'planned_revenue_mrc')
    def _compute_renew_mrr(self):
        for rec in self:
            rec.planned_revenue_renew_mrc = \
                rec.planned_revenue_mrc - rec.planned_revenue_new_mrc

    @api.multi
    @api.depends('planned_revenue_new_mrc')
    def _compute_new_planned_revenue(self):
        for rec in self:
            rec.new_planned_revenue = \
                rec.planned_revenue_new_mrc * rec.planned_duration

    @api.multi
    @api.depends('planned_revenue_new_mrc')
    def _compute_new_wieghted_revenue(self):
        for rec in self:
            rec.new_weighted_revenue = \
                rec.new_planned_revenue * rec.probability / 100

    @api.multi
    @api.depends('planned_revenue_new_mrc', 'planned_revenue_renew_mrc',
                 'new_planned_revenue', 'new_weighted_revenue')
    def _compute_new_planned_revenue_currency(self):
        for rec in self:
            rec.planned_revenue_new_mrc_usd = rec.currency_id.compute(
                rec.planned_revenue_new_mrc, rec.currency_usd_id
            )
            rec.planned_revenue_renew_mrc_usd = rec.currency_id.compute(
                rec.planned_revenue_renew_mrc, rec.currency_usd_id
            )
            rec.new_planned_revenue_usd = rec.currency_id.compute(
                rec.new_planned_revenue, rec.currency_usd_id
            )
            rec.new_weighted_revenue_usd = rec.currency_id.compute(
                rec.new_weighted_revenue, rec.currency_usd_id
            )
            rec.planned_revenue_new_mrc_eur = rec.currency_id.compute(
                rec.planned_revenue_new_mrc, rec.currency_eur_id
            )
            rec.planned_revenue_renew_mrc_eur = rec.currency_id.compute(
                rec.planned_revenue_renew_mrc, rec.currency_eur_id
            )
            rec.new_planned_revenue_eur = rec.currency_id.compute(
                rec.new_planned_revenue, rec.currency_eur_id
            )
            rec.new_weighted_revenue_eur = rec.currency_id.compute(
                rec.new_weighted_revenue, rec.currency_eur_id
            )

    @api.multi
    @api.depends('planned_revenue_new_mrc', 'planned_revenue_renew_mrc',
                 'new_planned_revenue', 'new_weighted_revenue')
    def _compute_display_planned_new_revenues(self):
        if self.env.user.company_id.currency_id == self.env.ref('base.USD'):
            for opp in self:
                opp.update({
                    'display_planned_revenue_new_mrc':
                        opp.planned_revenue_new_mrc_usd,
                    'display_planned_revenue_renew_mrc':
                        opp.planned_revenue_renew_mrc_usd,
                    'display_new_planned_revenue':
                        opp.new_planned_revenue_usd,
                    'display_new_weighted_revenue':
                        opp.new_weighted_revenue_usd,
                })
        else:
            for opp in self:
                opp.update({
                    'display_planned_revenue_new_mrc':
                        opp.planned_revenue_new_mrc_eur,
                    'display_planned_revenue_renew_mrc':
                        opp.planned_revenue_renew_mrc_eur,
                    'display_new_planned_revenue':
                        opp.new_planned_revenue_eur,
                    'display_new_weighted_revenue':
                        opp.new_weighted_revenue_eur,
                })
