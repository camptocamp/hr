# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SalespersonCommissionQuarter(models.Model):
    _name = 'salesperson.commission.quarter'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Selection(
        string='Quarter',
        selection=[
            ('Q1', 'Q1'),
            ('Q2', 'Q2'),
            ('Q3', 'Q3'),
            ('Q4', 'Q4')
        ],
    )
    user_id = fields.Many2one(
        string='Salesperson',
        comodel_name='res.users'
    )
    year = fields.Integer(
        string='Year',
    )
    target_id = fields.Many2one(
        string='Target',
        comodel_name='sale.target',
    )
    target_nrr = fields.Monetary(
        string='Target NRR',
        related='target_id.quarter_target_nrr',
        readonly=True,
        store=True,
    )
    target_mrr = fields.Monetary(
        string='Target MRR',
        related='target_id.quarter_target_mrr',
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='target_id.currency_id',
        readonly=True,
        store=True,
    )
    commission_lines = fields.One2many(
        string='Commission Lines',
        comodel_name='salesperson.commission.line',
        inverse_name='quarter_id',
        domain=[('order_id.state', 'in', ('sale', 'done'))],
    )
    earnings_nrr = fields.Monetary(
        string='Earnings NRR',
        compute='_compute_earnings_nrr',
        store=True
    )
    earnings_mrr = fields.Monetary(
        string='Earnings MRR',
        compute='_compute_earnings_mrr',
        store=True
    )
    attainment_ratio_nrr = fields.Float(
        string='Attainment Ratio NRR',
        compute='_compute_attainment_ratio_nrr',
        store=True
    )
    attainment_ratio_mrr = fields.Float(
        string='Attainment Ratio MRR',
        compute='_compute_attainment_ratio_mrr',
        store=True
    )
    attainment_factor_nrr = fields.Float(
        string='Attainment Factor NRR',
        compute='_compute_attainment_factor_nrr',
        store=True
    )
    attainment_factor_mrr = fields.Float(
        string='Attainment Factor MRR',
        compute='_compute_attainment_factor_mrr',
        store=True
    )
    commission_nrr = fields.Monetary(
        string='Commission NRR',
        compute='_compute_commission_nrr',
        store=True
    )
    commission_mrr = fields.Monetary(
        string='Commission MRR',
        compute='_compute_commission_mrr',
        store=True
    )
    commission = fields.Monetary(
        string='Commission',
        compute='_compute_commission',
        store=True
    )
    payout_nrr = fields.Monetary(
        string='Payout NRR',
        compute='_compute_payout_nrr',
        store=True
    )
    payout_mrr = fields.Monetary(
        string='Payout MRR',
        compute='_compute_payout_mrr',
        store=True
    )
    payout = fields.Monetary(
        string='Payout',
        compute='_compute_payout',
        store=True
    )
    annual_id = fields.Many2one(
        string='Annual Commission',
        comodel_name='salesperson.commission.annual',
        ondelete='cascade'
    )
    _sql_constraints = [
        ('year_user_id_name_uniq', 'UNIQUE(year, user_id, name)',
         'A Commission quarter already exists for this Salesperson,\
          in this year, in this quarter'),
    ]

    @api.depends('commission_lines.earnings_nrr')
    def _compute_earnings_nrr(self):
        for rec in self:
            rec.earnings_nrr = sum(rec.commission_lines.mapped('earnings_nrr'))

    @api.depends('commission_lines.earnings_mrr')
    def _compute_earnings_mrr(self):
        for rec in self:
            rec.earnings_mrr = sum(rec.commission_lines.mapped('earnings_mrr'))

    @api.depends('earnings_nrr', 'target_nrr')
    def _compute_attainment_ratio_nrr(self):
        for rec in self:
            if rec.target_nrr:
                rec.attainment_ratio_nrr = rec.earnings_nrr / rec.target_nrr

    @api.depends('earnings_mrr', 'target_mrr')
    def _compute_attainment_ratio_mrr(self):
        for rec in self:
            if rec.target_mrr:
                rec.attainment_ratio_mrr = rec.earnings_mrr / rec.target_mrr

    @api.depends('attainment_ratio_nrr')
    def _compute_attainment_factor_nrr(self):
        for rec in self:
            if rec.attainment_ratio_nrr:
                rec.attainment_factor_nrr = self._get_attainment_factor(
                    rec.attainment_ratio_nrr)

    @api.depends('attainment_ratio_mrr')
    def _compute_attainment_factor_mrr(self):
        for rec in self:
            if rec.attainment_ratio_mrr:
                rec.attainment_factor_mrr = self._get_attainment_factor(
                    rec.attainment_ratio_mrr)

    def _get_attainment_factor(self, attainment_ratio):
        parameters = self.env['sales.commission.settings'].get()
        if attainment_ratio <= 0.5:
            return parameters.attainment_factor_0
        if attainment_ratio <= 1:
            return parameters.attainment_factor_50
        return parameters.attainment_factor_100

    @api.depends('commission_lines.commission_nrr')
    def _compute_commission_nrr(self):
        for rec in self:
            rec.commission_nrr = sum(
                rec.commission_lines.mapped('commission_nrr'))

    @api.depends('commission_lines.commission_mrr')
    def _compute_commission_mrr(self):
        for rec in self:
            rec.commission_mrr = sum(
                rec.commission_lines.mapped('commission_mrr'))

    @api.depends('commission_mrr', 'commission_nrr')
    def _compute_commission(self):
        for rec in self:
            rec.commission = rec.commission_mrr + rec.commission_nrr

    @api.depends('commission_nrr', 'attainment_factor_nrr')
    def _compute_payout_nrr(self):
        for rec in self:
            rec.payout_nrr = rec.commission_nrr * rec.attainment_factor_nrr

    @api.depends('commission_mrr', 'attainment_factor_mrr')
    def _compute_payout_mrr(self):
        for rec in self:
            rec.payout_mrr = rec.commission_mrr * rec.attainment_factor_mrr

    @api.depends('payout_mrr', 'payout_nrr')
    def _compute_payout(self):
        for rec in self:
            rec.payout = rec.payout_mrr + rec.payout_nrr

    @api.model
    def create(self, values):
        rec = super(SalespersonCommissionQuarter, self).create(values)
        annual_id = rec.annual_id.search([
            ('user_id', '=', rec.user_id.id),
            ('year', '=', rec.year),
        ])
        if not annual_id:
            annual_id = rec.annual_id.sudo().create({
                'user_id': rec.user_id.id,
                'year': rec.year,
                'target_id': rec.target_id.id,
            })
        rec.write({'annual_id': annual_id.id})
        return rec
