# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # technical fields, used to supply info to views
    currency_usd_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_technical_currencies',
    )
    currency_eur_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_technical_currencies',
    )
    currency_company_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_technical_currencies',
        help='An ugly technical field to display proper currency in a tree',
    )

    currency_id = fields.Many2one(
        required=True,
        comodel_name='res.currency',
        string='Opportunity currency',
        default=lambda self: self._default_currency_id(),
    )
    planned_duration = fields.Integer(
        'Duration',
        track_visibility='always',
    )

    industry_id = fields.Many2one(
        string="Industry",
        comodel_name="crm.industry",
    )
    industry_subsector_id = fields.Many2one(
        string="Industry Subsector",
        comodel_name="crm.industry.subsector",
        domain="[('industry_id', '=', industry_id)]",
    )
    status = fields.Selection(
        string="Status",
        selection="_status_selection",
    )
    quick_title_id = fields.Many2one(
        string="Quicktitle",
        comodel_name="crm.lead.quicktitle",
    )
    company_type = fields.Selection(
        string="Company Type",
        selection="_company_type_selection",
    )
    size = fields.Selection(
        string="Size",
        selection="_size_selection",
    )
    original_lead_id = fields.Many2one(
        string="Original Lead",
        comodel_name="crm.lead",
        copy=False,
    )
    child_leads_ids = fields.One2many(
        string="Child leads",
        comodel_name="crm.lead",
        inverse_name="original_lead_id",
    )
    commercial_partner_id = fields.Many2one(
        related="partner_id.commercial_partner_id",
        readonly=True,
        store=True,
        index=True,
    )
    original_lead_commercial_partner_id = fields.Many2one(
        related="original_lead_id.partner_id",
        readonly=True,
        store=True,
        copy=False,
    )
    has_child_leads = fields.Boolean(
        string="Has child leads",
        compute="_compute_has_child_leads",
    )

    # Regular revenue fields (in the currency of opportunity)
    planned_revenue = fields.Float(
        string='TCV',
        help='Total Contract Value',
        compute='_compute_planned_revenue',
        currency_field='currency_id',
    )
    planned_revenue_nrc = fields.Monetary(
        string='NRC',
        help='Expected NRC Revenue',
        track_visibility='always',
        currency_field='currency_id',
    )
    planned_revenue_mrc = fields.Monetary(
        string='MRC',
        help='Expected MRC Revenue',
        track_visibility='always',
        currency_field='currency_id',
    )
    weighted_revenue = fields.Monetary(
        string='Adjusted TCV',
        compute='_compute_planned_revenue',
        currency_field='currency_id',
    )
    sum_planned_revenue_nrc = fields.Float(
        string="Sum planned revenue nrc",
        compute="_compute_sum_nrc_mrc",
    )
    sum_planned_revenue_mrc = fields.Float(
        string="Sum planned revenue mrc",
        compute="_compute_sum_nrc_mrc",
    )

    # Converted fields (each is also represented in EUR and USD)
    planned_revenue_nrc_eur = fields.Monetary(
        string='Expected NRC Revenue (EUR)',
        compute='_compute_planned_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_revenue_nrc_usd = fields.Monetary(
        string='Expected NRC Revenue (USD)',
        compute='_compute_planned_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    planned_revenue_mrc_eur = fields.Monetary(
        string='Expected MRC Revenue (EUR)',
        compute='_compute_planned_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_revenue_mrc_usd = fields.Monetary(
        string='Expected MRC Revenue (USD)',
        compute='_compute_planned_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    planned_revenue_eur = fields.Monetary(
        string='Expected Revenue (EUR)',
        compute='_compute_planned_revenue',
        currency_field='currency_eur_id',
        store=True,
    )
    planned_revenue_usd = fields.Monetary(
        string='Expected Revenue (USD)',
        compute='_compute_planned_revenue',
        currency_field='currency_usd_id',
        store=True,
    )
    weighted_revenue_eur = fields.Monetary(
        string='Adjusted TCV (EUR)',
        compute='_compute_planned_revenue',
        currency_field='currency_eur_id',
    )
    weighted_revenue_usd = fields.Monetary(
        string='Adjusted TCV (USD)',
        compute='_compute_planned_revenue',
        currency_field='currency_usd_id',
    )

    # Used conversion rates
    rate_opportunity_to_eur = fields.Float(
        digits=(12, 6),
    )
    rate_opportunity_to_usd = fields.Float(
        digits=(12, 6),
    )
    rate_opportunity_to_company = fields.Float(
        digits=(12, 6),
    )

    # used only to display the proper one on a tree view
    display_planned_revenue = fields.Monetary(
        string='Expected Revenue',
        compute='_compute_display_planned_revenues',
        currency_field='currency_company_id',
    )
    display_planned_revenue_nrc = fields.Monetary(
        string='NRC',
        compute='_compute_display_planned_revenues',
        currency_field='currency_company_id',
    )
    display_planned_revenue_mrc = fields.Monetary(
        string='MRC',
        compute='_compute_display_planned_revenues',
        currency_field='currency_company_id',
    )
    display_weighted_tcv = fields.Monetary(
        string='Adjusted TCV',
        compute='_compute_display_planned_revenues',
        currency_field='currency_company_id',
    )

    def _default_currency_id(self):
        return self.company_currency or self.env.user.company_id.currency_id.id

    @api.multi
    def _compute_technical_currencies(self):
        self.update({
            'currency_company_id': self.env.user.company_id.currency_id,
            'currency_eur_id': self.env.ref('base.EUR'),
            'currency_usd_id': self.env.ref('base.USD'),
        })

    @api.multi
    @api.depends(
        'planned_revenue_usd',
        'planned_revenue_mrc_usd',
        'planned_revenue_nrc_usd',
        'planned_revenue_eur',
        'planned_revenue_mrc_eur',
        'planned_revenue_nrc_eur',
        'weighted_revenue_usd',
        'weighted_revenue_eur',
    )
    def _compute_display_planned_revenues(self):
        # Purpose:
        # display revenues in USD if it is current user company's main currency
        # otherwise, display revenues in EUR
        if self.env.user.company_id.currency_id == self.env.ref('base.USD'):
            for opp in self:
                opp.update({
                    'display_planned_revenue': opp.planned_revenue_usd,
                    'display_planned_revenue_mrc': opp.planned_revenue_mrc_usd,
                    'display_planned_revenue_nrc': opp.planned_revenue_nrc_usd,
                    'display_weighted_tcv': opp.weighted_revenue_usd,
                })
        else:
            for opp in self:
                opp.update({
                    'display_planned_revenue': opp.planned_revenue_eur,
                    'display_planned_revenue_mrc': opp.planned_revenue_mrc_eur,
                    'display_planned_revenue_nrc': opp.planned_revenue_nrc_eur,
                    'display_weighted_tcv': opp.weighted_revenue_eur,
                })

    @api.multi
    @api.depends('child_leads_ids')
    def _compute_sum_nrc_mrc(self):
        for record in self:
            if not record.has_child_leads:
                continue
            else:
                child_leads = record.child_leads_ids
                record.sum_planned_revenue_nrc = sum(
                    child_leads.mapped('planned_revenue_nrc')
                )
                record.sum_planned_revenue_mrc = sum(
                    child_leads.mapped('planned_revenue_mrc')
                )

    @api.multi
    @api.depends('child_leads_ids')
    def _compute_has_child_leads(self):
        for record in self:
            record.has_child_leads = bool(record.child_leads_ids)

    def _status_selection(self):
        return [
            ('not_relevant', 'Not Relevant'),
            ('priority', 'Priority'),
        ]

    def _company_type_selection(self):
        return [
            ('global', 'Global'),
            ('national', 'National'),
        ]

    def _size_selection(self):
        return [
            ('small', 'Small'),
            ('medium', 'Medium'),
            ('large', 'Large'),
        ]

    @api.multi
    @api.depends(
        'planned_duration',
        'planned_revenue_mrc',
        'planned_revenue_nrc',
        'company_currency',
        'currency_id',
        'probability',
    )
    def _compute_planned_revenue(self):
        def get_rate_to(from_curr, to_curr):
            self.env['res.currency']._get_conversion_rate(from_curr, to_curr)

        for rec in self:
            planned_revenue = (
                rec.planned_revenue_nrc
                + (rec.planned_revenue_mrc * rec.planned_duration)
            )
            weighted_revenue = planned_revenue * rec.probability / 100
            weighted_revenue_eur = rec.currency_id.compute(
                weighted_revenue, rec.currency_eur_id)
            weighted_revenue_usd = rec.currency_id.compute(
                weighted_revenue, rec.currency_usd_id)
            rec.update({
                'planned_revenue': planned_revenue,
                'weighted_revenue': weighted_revenue,
                'weighted_revenue_usd': weighted_revenue_usd,
                'weighted_revenue_eur': weighted_revenue_eur,
            })

            from_nrc = rec.planned_revenue_nrc
            nrc_amount_eur = rec.currency_id.compute(
                from_nrc, rec.currency_eur_id)
            nrc_amount_usd = rec.currency_id.compute(
                from_nrc, rec.currency_usd_id)

            from_mrc = rec.planned_revenue_mrc
            mrc_amount_eur = rec.currency_id.compute(
                from_mrc, rec.currency_eur_id)
            mrc_amount_usd = rec.currency_id.compute(
                from_mrc, rec.currency_usd_id)

            from_total = rec.planned_revenue
            total_amount_eur = rec.currency_id.compute(
                from_total, rec.currency_eur_id)
            total_amount_usd = rec.currency_id.compute(
                from_total, rec.currency_usd_id)

            rec.update({
                'planned_revenue_eur': total_amount_eur,
                'planned_revenue_usd': total_amount_usd,
                # NRC
                'planned_revenue_nrc_eur': nrc_amount_eur,
                'planned_revenue_nrc_usd': nrc_amount_usd,
                # MRC
                'planned_revenue_mrc_eur': mrc_amount_eur,
                'planned_revenue_mrc_usd': mrc_amount_usd,
                # freeze conversion rates
                'rate_opportunity_to_eur': get_rate_to(
                    rec.currency_id, rec.currency_eur_id),
                'rate_opportunity_to_usd': get_rate_to(
                    rec.currency_id, rec.currency_usd_id),
                'rate_opportunity_to_company': get_rate_to(
                    rec.currency_id, rec.currency_company_id),
            })

    @api.multi
    def action_update_rates(self):
        """Trigger recalculation of converted revenues manually."""
        self._compute_planned_revenue()

    @api.multi
    def action_view_opportunities(self):
        self.ensure_one()

        form_view = self.env.ref('crm.crm_case_form_view_oppor')
        tree_view = self.env.ref('crm.crm_case_tree_view_oppor')
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'crm.lead',
            'domain': [
                '&',
                ('type', '=', 'opportunity'),
                ('id', 'in', self.child_leads_ids.ids),
            ],
            'res_id': self.id,
            'view_id': False,
            'views': [
                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
                (False, 'kanban'),
                (False, 'calendar'),
                (False, 'graph')
            ],
            'type': 'ir.actions.act_window',
            'context': {'default_type': 'opportunity'}
        }
