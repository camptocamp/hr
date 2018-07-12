# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    planned_revenue_nrc = fields.Monetary(
        'Expected NRC Revenue',
        track_visibility='always',
        currency_field='currency_id',
    )
    planned_revenue_mrc = fields.Monetary(
        'Expected MRC Revenue',
        track_visibility='always',
        currency_field='currency_id',
    )

    planned_revenue_currency = fields.Monetary(
        string='Expected revenue (opportunity currency)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_id',
        digits=(16, 2),
    )
    planned_revenue_eur = fields.Monetary(
        string='Expected Revenue (EUR)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_eur_id',
        store=True,
        digits=(16, 2),
    )
    planned_revenue_nrc_eur = fields.Monetary(
        string='Expected NRC Revenue (EUR)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_eur_id',
        store=True,
        digits=(16, 2),
    )
    planned_revenue_mrc_eur = fields.Monetary(
        string='Expected MRC Revenue (EUR)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_eur_id',
        store=True,
        digits=(16, 2),
    )

    planned_revenue_usd = fields.Monetary(
        string='Expected Revenue (USD)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_usd_id',
        store=True,
        digits=(16, 2),
    )
    planned_revenue_nrc_usd = fields.Monetary(
        string='Expected NRC Revenue (USD)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_usd_id',
        store=True,
        digits=(16, 2),
    )
    planned_revenue_mrc_usd = fields.Monetary(
        string='Expected MRC Revenue (USD)',
        compute='_compute_converted_eur_usd_revenues',
        currency_field='currency_usd_id',
        store=True,
        digits=(16, 2),
    )

    # used only to display the proper one on a tree view
    display_planned_revenue = fields.Monetary(
        string='Expected Revenue',
        compute='_compute_technical_currencies',
        currency_field='currency_company_id',
        digits=(16, 2),
    )
    display_planned_revenue_nrc = fields.Monetary(
        string='Expected NRC Revenue',
        compute='_compute_technical_currencies',
        currency_field='currency_company_id',
        digits=(16, 2),
    )
    display_planned_revenue_mrc = fields.Monetary(
        string='Expected MRC Revenue',
        compute='_compute_technical_currencies',
        currency_field='currency_company_id',
        digits=(16, 2),
    )

    rate_opportunity_to_eur = fields.Float()
    rate_opportunity_to_usd = fields.Float()
    rate_opportunity_to_company = fields.Float()

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
    planned_revenue = fields.Float(
        'Expected Revenue',
        compute='_compute_planned_revenue',
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
    sum_planned_revenue_nrc = fields.Float(
        string="Sum planned revenue nrc",
        compute="_compute_sum_nrc_mrc",
    )
    sum_planned_revenue_mrc = fields.Float(
        string="Sum planned revenue mrc",
        compute="_compute_sum_nrc_mrc",
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
        # Purpose:
        # display values in USD if it is current user company's main currency
        # otherwise, display EUR currencies
        if self.env.user.company_id.currency_id == self.env.ref('base.USD'):
            for opp in self:
                opp.update({
                    'display_planned_revenue': opp.planned_revenue_usd,
                    'display_planned_revenue_mrc': opp.planned_revenue_mrc_usd,
                    'display_planned_revenue_nrc': opp.planned_revenue_nrc_usd,
                })
        else:
            for opp in self:
                opp.update({
                    'display_planned_revenue': opp.planned_revenue_eur,
                    'display_planned_revenue_mrc': opp.planned_revenue_mrc_eur,
                    'display_planned_revenue_nrc': opp.planned_revenue_nrc_eur,
                })

    @api.multi
    @api.depends(
        'planned_revenue_nrc',
        'planned_revenue_mrc',
        'currency_id',
        'planned_duration',
    )
    def _compute_converted_eur_usd_revenues(self):
        def get_rate_to(from_curr, to_curr):
            self.env['res.currency']._get_conversion_rate(from_curr, to_curr)

        for lead in self:
            from_nrc = lead.planned_revenue_nrc
            nrc_amount_eur = lead.currency_id.compute(
                from_nrc, lead.currency_eur_id)
            nrc_amount_usd = lead.currency_id.compute(
                from_nrc, lead.currency_usd_id)

            from_mrc = lead.planned_revenue_mrc
            mrc_amount_eur = lead.currency_id.compute(
                from_mrc, lead.currency_eur_id)
            mrc_amount_usd = lead.currency_id.compute(
                from_mrc, lead.currency_usd_id)

            from_total = lead.planned_revenue
            total_amount_eur = lead.currency_id.compute(
                from_total, lead.currency_eur_id)
            total_amount_usd = lead.currency_id.compute(
                from_total, lead.currency_usd_id)

            lead.update({
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
                    lead.currency_id, lead.currency_eur_id),
                'rate_opportunity_to_usd': get_rate_to(
                    lead.currency_id, lead.currency_usd_id),
                'rate_opportunity_to_company': get_rate_to(
                    lead.currency_id, lead.currency_company_id),
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

    @api.depends(
        'planned_duration',
        'planned_revenue_mrc',
        'planned_revenue_nrc',
    )
    def _compute_planned_revenue(self):
        for rec in self:
            planned_revenue = (
                rec.planned_revenue_nrc
                + (rec.planned_revenue_mrc * rec.planned_duration)
            )
            rec.update({
                'planned_revenue': planned_revenue,
                'planned_revenue_currency': rec.company_currency.compute(
                    planned_revenue, rec.currency_id),
            })

    @api.multi
    def action_update_rates(self):
        self._compute_converted_eur_usd_revenues()

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
