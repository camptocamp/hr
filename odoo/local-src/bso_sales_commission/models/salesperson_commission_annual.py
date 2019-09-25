# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SalespersonCommissionAnnual(models.Model):
    _name = 'salesperson.commission.annual'
    _rec_name = 'year'

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
        related='target_id.annual_target_nrr',
        readonly=True,
        store=True,
    )
    target_mrr = fields.Monetary(
        string='Target MRR',
        related='target_id.annual_target_mrr',
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='target_id.currency_id',
        readonly=True,
        store=True,
    )
    commission_quarters = fields.One2many(
        string='Quarter Commission',
        comodel_name='salesperson.commission.quarter',
        inverse_name='annual_id'
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
    payout_nrr = fields.Float(
        string='Total Payout NRR',
        compute='_compute_payout_nrr',
        store=True
    )
    payout_mrr = fields.Float(
        string='Total Payout MRR',
        compute='_compute_payout_mrr',
        store=True
    )
    payout = fields.Float(
        string='Total Payout',
        compute='_compute_payout',
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
        string='Total Commission',
        compute='_compute_commission',
        store=True
    )
    _sql_constraints = [
        ('year_user_id_uniq', 'UNIQUE(year, user_id)',
         'A Commission annual already exists for this Salesperson'),
    ]

    @api.depends('commission_quarters.earnings_nrr')
    def _compute_earnings_nrr(self):
        for rec in self:
            rec.earnings_nrr = sum(
                rec.commission_quarters.mapped('earnings_nrr'))

    @api.depends('commission_quarters.earnings_mrr')
    def _compute_earnings_mrr(self):
        for rec in self:
            rec.earnings_mrr = sum(
                rec.commission_quarters.mapped('earnings_mrr'))

    @api.depends('commission_quarters.payout_nrr')
    def _compute_payout_nrr(self):
        for rec in self:
            rec.payout_nrr = sum(rec.commission_quarters.mapped(
                'payout_nrr'))

    @api.depends('commission_quarters.payout_mrr')
    def _compute_payout_mrr(self):
        for rec in self:
            rec.payout_mrr = sum(
                rec.commission_quarters.mapped('payout_mrr'))

    @api.depends('payout_mrr', 'payout_nrr')
    def _compute_payout(self):
        for rec in self:
            rec.payout = \
                rec.payout_mrr + rec.payout_nrr

    @api.depends('commission_quarters.commission_nrr')
    def _compute_commission_nrr(self):
        for rec in self:
            rec.commission_nrr = sum(rec.commission_quarters.mapped(
                'commission_nrr'))

    @api.depends('commission_quarters.commission_mrr')
    def _compute_commission_mrr(self):
        for rec in self:
            rec.commission_mrr = sum(
                rec.commission_quarters.mapped('commission_mrr'))

    @api.depends('commission_mrr', 'commission_nrr')
    def _compute_commission(self):
        for rec in self:
            rec.commission = \
                rec.commission_mrr + rec.commission_nrr
