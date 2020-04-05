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
    category_id = fields.Many2one(
        string='Category',
        comodel_name='product.category'
    )

    planned_new_revenue = fields.Monetary(
        string='New TCV',
        help='New Total Contract Value',
        compute='_compute_planned_new_revenue',
        currency_field='currency_id',
        store=True,
    )
    planned_revenue_new_mrc = fields.Monetary(
        string='New MRC',
        help='Expected New MRC Revenue',
        compute='_compute_new_mrr',
        currency_field='currency_id',
        track_visibility='always',
        store=True,
    )
    planned_revenue_renew_mrc = fields.Monetary(
        string='Renewal MRC',
        help='Expected Renewal MRC Revenue',
        track_visibility='always',
        currency_field='currency_id',
    )

    weighted_new_revenue = fields.Monetary(
        string='Adjusted New TCV',
        compute='_compute_planned_new_revenue',
        currency_field='currency_id',
        store=True,
    )
    sum_planned_revenue_new_mrc = fields.Float(
        string="Sum planned revenue new mrc",
        compute="_compute_sum_new_renew",
    )
    sum_planned_revenue_renew_mrc = fields.Float(
        string="Sum planned revenue renew mrc",
        compute="_compute_sum_new_renew",
    )

    planned_revenue_new_mrc_eur = fields.Monetary(
        string='Expected New MRC Revenue (EUR)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_revenue_new_mrc_usd = fields.Monetary(
        string='Expected New MRC Revenue (USD)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    planned_revenue_renew_mrc_eur = fields.Monetary(
        string='Expected Renewal MRC Revenue (EUR)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_revenue_renew_mrc_usd = fields.Monetary(
        string='Expected Renewal MRC Revenue (USD)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    planned_new_revenue_eur = fields.Monetary(
        string='Expected New Revenue (EUR)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_new_revenue_usd = fields.Monetary(
        string='Expected New Revenue (USD)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    weighted_new_revenue_eur = fields.Monetary(
        string='Adjusted New TCV (EUR)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    weighted_new_revenue_usd = fields.Monetary(
        string='Adjusted New TCV (USD)',
        compute='_compute_planned_new_revenue',
        currency_field='currency_usd_id',
        store=True,
    )

    display_planned_new_revenue = fields.Monetary(
        string='Expected New Revenue',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_company_id',
    )
    display_planned_revenue_new_mrc = fields.Monetary(
        string='New MRC',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_company_id',
    )
    display_planned_revenue_renew_mrc = fields.Monetary(
        string='Renew MRC',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_company_id',
    )
    display_weighted_new_revenue = fields.Monetary(
        string='Adjusted New TCV',
        compute='_compute_display_planned_new_revenues',
        currency_field='currency_company_id',
    )

    @api.multi
    @api.depends('child_leads_ids')
    def _compute_sum_nrc_mrc(self):
        for record in self:
            if not record.has_child_leads:
                continue
            else:
                child_leads = record.child_leads_ids
                record.sum_planned_revenue_new_mrc = sum(
                    child_leads.mapped('planned_revenue_new_mrc')
                )
                record.sum_planned_revenue_renew_mrc = sum(
                    child_leads.mapped('planned_revenue_renew_mrc')
                )

    @api.multi
    @api.depends('planned_revenue_mrc', 'planned_revenue_renew_mrc')
    def _compute_new_mrr(self):
        for rec in self:
            rec.planned_revenue_new_mrc = \
                rec.planned_revenue_mrc - rec.planned_revenue_renew_mrc

    @api.multi
    @api.depends(
        'planned_duration',
        'planned_revenue_nrc',
        'planned_revenue_new_mrc',
        'planned_revenue_renew_mrc',
        'company_currency',
        'currency_id',
        'probability',
    )
    def _compute_planned_new_revenue(self):
        for rec in self:
            planned_new_revenue = (
                rec.planned_revenue_nrc
                + (rec.planned_revenue_new_mrc * rec.planned_duration)
            )
            planned_new_revenue_eur = rec.currency_id.compute(
                planned_new_revenue, rec.currency_eur_id)
            planned_new_revenue_usd = rec.currency_id.compute(
                planned_new_revenue, rec.currency_usd_id)
            weighted_new_revenue = planned_new_revenue * rec.probability / 100
            weighted_new_revenue_eur = rec.currency_id.compute(
                weighted_new_revenue, rec.currency_eur_id)
            weighted_new_revenue_usd = rec.currency_id.compute(
                weighted_new_revenue, rec.currency_usd_id)
            rec.update({
                'planned_new_revenue': planned_new_revenue,
                'planned_new_revenue_eur': planned_new_revenue_eur,
                'planned_new_revenue_usd': planned_new_revenue_usd,
                'weighted_new_revenue': weighted_new_revenue,
                'weighted_new_revenue_usd': weighted_new_revenue_usd,
                'weighted_new_revenue_eur': weighted_new_revenue_eur,
            })

            from_new_mrc = rec.planned_revenue_new_mrc
            new_mrc_amount_eur = rec.currency_id.compute(
                from_new_mrc, rec.currency_eur_id)
            new_mrc_amount_usd = rec.currency_id.compute(
                from_new_mrc, rec.currency_usd_id)

            from_renew_mrc = rec.planned_revenue_renew_mrc
            renew_mrc_amount_eur = rec.currency_id.compute(
                from_renew_mrc, rec.currency_eur_id)
            renew_mrc_amount_usd = rec.currency_id.compute(
                from_renew_mrc, rec.currency_usd_id)

            rec.update({
                'planned_revenue_new_mrc_eur': new_mrc_amount_eur,
                'planned_revenue_new_mrc_usd': new_mrc_amount_usd,
                'planned_revenue_renew_mrc_eur': renew_mrc_amount_eur,
                'planned_revenue_renew_mrc_usd': renew_mrc_amount_usd,
            })

    @api.multi
    @api.depends('planned_revenue_new_mrc', 'planned_revenue_renew_mrc',
                 'planned_new_revenue', 'weighted_new_revenue')
    def _compute_display_planned_new_revenues(self):
        if self.env.user.company_id.currency_id == self.env.ref('base.USD'):
            for opp in self:
                opp.update({
                    'display_planned_revenue_new_mrc':
                        opp.planned_revenue_new_mrc_usd,
                    'display_planned_revenue_renew_mrc':
                        opp.planned_revenue_renew_mrc_usd,
                    'display_planned_new_revenue':
                        opp.planned_new_revenue_usd,
                    'display_weighted_new_revenue':
                        opp.weighted_new_revenue_usd,
                })
        else:
            for opp in self:
                opp.update({
                    'display_planned_revenue_new_mrc':
                        opp.planned_revenue_new_mrc_eur,
                    'display_planned_revenue_renew_mrc':
                        opp.planned_revenue_renew_mrc_eur,
                    'display_planned_new_revenue':
                        opp.planned_new_revenue_eur,
                    'display_weighted_new_revenue':
                        opp.weighted_new_revenue_eur,
                })

    @api.multi
    def action_update_rates(self):
        """Trigger recalculation of converted revenues manually."""
        super(CrmLeads, self).action_update_rates()
        self._compute_planned_new_revenue()
