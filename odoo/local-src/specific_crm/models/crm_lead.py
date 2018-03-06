# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planned_revenue_nrc = fields.Float(
        'Expected NRC Revenue',
        track_visibility='always',
    )
    planned_revenue_mrc = fields.Float(
        'Expected MRC Revenue',
        track_visibility='always',
    )
    planned_duration = fields.Integer(
        'Duration',
        track_visibility='always',
    )
    planned_revenue = fields.Float(
        'Expected Revenue',
        compute='_get_planned_revenue',
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
    sum_quotes = fields.Float(
        string="Sum qoutes",
        compute="_compute_sum_quotes_sales",
    )
    sum_sales = fields.Float(
        string="Sum sales",
        compute="_compute_sum_quotes_sales",
    )

    @api.multi
    def _compute_sum_quotes_sales(self):
        for record in self:
            sales = record._get_so()
            quotes = record._get_quotes()
            record.sum_sales = sum(sales.mapped('amount_total'))
            record.sum_quotes = sum(quotes.mapped('amount_total'))

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

    @api.depends('planned_duration',
                 'planned_revenue_mrc',
                 'planned_revenue_nrc')
    def _get_planned_revenue(self):
        for rec in self:
            rec.planned_revenue = (
                rec.planned_revenue_nrc +
                (rec.planned_revenue_mrc * rec.planned_duration)
            )

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

    def _get_quotes(self):
        self.ensure_one()
        quotations = self.env['sale.order'].search([
            '&',
            ('state', '=', 'draft'),
            ('partner_id.commercial_partner_id', '=', self.partner_id.id),
        ])
        return quotations

    def _get_so(self):
        self.ensure_one()
        sale_orders = self.env['sale.order'].search([
            '&',
            ('state', '!=', 'draft'),
            ('partner_id.commercial_partner_id', '=', self.partner_id.id),
        ])
        return sale_orders

    @api.multi
    def action_view_quotations(self):
        self.ensure_one()
        quotations = self._get_quotes()
        return {
            "name": _("Quotes"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [('id', 'in', quotations.ids)],
            "context": {"create": False, "show_sale": True},
        }

    @api.multi
    def action_view_so(self):
        self.ensure_one()
        sale_orders = self._get_so()
        return {
            "name": _("Sale Orders"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "tree,form",
            "domain": [('id', 'in', sale_orders.ids)],
            "context": {"create": False, "show_sale": True},
        }
