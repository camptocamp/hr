# -*- coding:utf-8 -*-

from odoo import models, fields, api, _


class SalespersonCommissionLine(models.Model):
    _name = 'salesperson.commission.line'
    _inherit = ['mail.thread']
    _rec_name = 'user_id'
    _sql_constraints = [('user_unique', 'unique(order_id, user_id)',
                         'Salesperson already exists')]

    user_id = fields.Many2one(
        string='Salesperson',
        comodel_name='res.users',
        required=True,
    )
    is_employed_in_fr = fields.Boolean(
        string='Is employed in France ',
        compute='_compute_is_employed_in_fr',
        store=True,
    )
    _percentage = fields.Float(
        string='Set Percentage',
        readonly=True,
    )
    percentage = fields.Float(
        string='Percentage',
        compute='_get_percentage',
        inverse='_set_percentage',
        store=True
    )
    manager_adjustment_nrr = fields.Float(
        string='Manager Adjustment NRR',
        track_visibility='onchange',
        default=1,
    )
    manager_adjustment_mrr = fields.Float(
        string='Manager Adjustment MRR',
        track_visibility='onchange',
        default=1,
    )
    is_main_salesperson = fields.Boolean(
        string='Is main salesperson',
        default=False,
        readonly=True,
    )
    order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        readonly=True,
        required=True,
    )
    duration = fields.Integer(
        string='Duration',
        related='order_id.duration',
        readonly=True,
        store=True,
    )
    confirmation_date = fields.Datetime(
        string='Confirmation date',
        related='order_id.confirmation_date',
        readonly=True,
        store=True,
    )
    subscription_management = fields.Selection(
        string='Subscription Management',
        related='order_id.subscription_management',
        readonly=True,
        store=True,
    )
    order_currency_id = fields.Many2one(
        string='Order Currency',
        related='order_id.currency_id',
        readonly=True,
        store=True
    )
    renewal_ratio = fields.Float(
        string='Renewal Ratio',
        compute='_compute_renewal_ratio',
        store=True,
    )
    renewal_factor = fields.Float(
        string='Renewal Factor',
        compute='_compute_renewal_factor',
        store=True,
    )
    year = fields.Integer(
        string='Year',
        compute='_compute_year',
        store=True
    )
    quarter = fields.Selection(
        string='Quarter',
        selection=[
            ('Q1', 'Q1'),
            ('Q2', 'Q2'),
            ('Q3', 'Q3'),
            ('Q4', 'Q4')
        ],
        compute='_compute_quarter',
        store=True
    )
    quarter_id = fields.Many2one(
        string='Commission Quarter',
        comodel_name='salesperson.commission.quarter',
        compute='_compute_quarter_id',
        store=True,
        ondelete='cascade',
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='quarter_id.target_id.currency_id',
        readonly=True,
        store=True,
    )
    margin_nrr = fields.Monetary(
        string='Margin NRR',
        compute='_compute_margin_nrr',
        store=True
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
    duration_factor = fields.Float(
        string='Duration Factor',
        compute='_compute_duration_factor',
        store=True,
    )
    nrm_factor = fields.Float(
        string='NRR Margin Factor',
        compute='_compute_nrm_factor',
        store=True,
    )
    mrr_factor = fields.Float(
        string='MRR Factor',
        compute='_compute_mrr_factor',
        store=True,
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
    exchange_rate_id = fields.Many2one(
        string='Exchange Rate',
        comodel_name='res.currency.rate',
        compute='_compute_exchange_rate_id',
        store=True
    )
    rate = fields.Float(
        string='Exchange Rate',
        compute='_compute_rate',
        digits=(12, 6),
        store=True
    )

    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
            if rec.percentage <= 0:
                if rec.is_main_salesperson:
                    raise Warning(_("Total Percentage exceeds 100%"))
                raise Warning(_("Percentage must be greater than 0"))

    @api.depends('user_id')
    def _compute_is_employed_in_fr(self):
        for rec in self:
            if rec.user_id.employee_ids.company_id.country_id.name == 'FRANCE':
                rec.is_employed_in_fr = True

    def _set_percentage(self):
        for rec in self:
            if rec.is_main_salesperson:
                rec._percentage = 0
            else:
                rec._percentage = rec.percentage

    @api.depends('order_id.salesperson_commission_line_ids._percentage')
    def _get_percentage(self):
        for rec in self:
            if rec.is_main_salesperson:
                lines = rec.order_id.salesperson_commission_line_ids
                rec.percentage = 100 - sum(lines.mapped('_percentage'))
            else:
                rec.percentage = rec._percentage

    @api.depends('confirmation_date')
    def _compute_year(self):
        for rec in self:
            if not rec.confirmation_date:
                continue
            rec.year = fields.Datetime.from_string(rec.confirmation_date).year

    @api.depends('confirmation_date')
    def _compute_renewal_ratio(self):
        for rec in self:
            if not rec.confirmation_date or not rec.order_id.project_id:
                continue
            cur_mrr = rec.order_id.project_id.subscription_ids.recurring_total
            new_mrr = rec.order_id.dealsheet_id.mrr
            rec.renewal_ratio = new_mrr / cur_mrr if cur_mrr else 1

    @api.depends('subscription_management', 'renewal_ratio')
    def _compute_renewal_factor(self):
        for rec in self:
            if rec.subscription_management == 'renew':
                rec.renewal_factor = rec._get_renewal_factor()
            else:
                rec.renewal_factor = 1

    def _get_renewal_factor(self):
        settings = self.env['sales.commission.settings'].get()
        if self.renewal_ratio < 0.9:
            return settings.renewal_factor_80
        if self.renewal_ratio < 1.0:
            return settings.renewal_factor_90
        return settings.renewal_factor_100

    @api.depends('duration')
    def _compute_duration_factor(self):
        for rec in self:
            rec.duration_factor = rec._get_duration_factor()

    def _get_duration_factor(self):
        settings = self.env['sales.commission.settings'].get()
        if self.duration < 24:
            return settings.duration_factor_12
        if self.duration < 36:
            return settings.duration_factor_24
        return settings.duration_factor_36

    @api.depends('order_id')
    def _compute_nrm_factor(self):
        settings = self.env['sales.commission.settings'].get()
        for rec in self:
            rec.nrm_factor = settings.nrm_factor

    @api.depends('is_employed_in_fr')
    def _compute_mrr_factor(self):
        settings = self.env['sales.commission.settings'].get()
        for rec in self:
            if rec.is_employed_in_fr:
                rec.mrr_factor = settings.mrr_factor_fr
            else:
                rec.mrr_factor = settings.mrr_factor

    @api.depends('confirmation_date')
    def _compute_quarter(self):
        for rec in self:
            if not rec.confirmation_date:
                continue
            so_month = fields.Date.from_string(
                rec.confirmation_date).month
            idx = (so_month - 1) // 3
            rec.quarter = 'Q%d' % (idx + 1)

    @api.depends('rate', 'earnings_nrr', 'order_id.dealsheet_id.nrm')
    def _compute_margin_nrr(self):
        for rec in self:
            nrm_percentage = rec.order_id.dealsheet_id.nrm
            margin_nrr = (rec.earnings_nrr * nrm_percentage) / 100
            rec.margin_nrr = margin_nrr * rec.rate

    @api.depends('rate', 'order_id.dealsheet_id.nrr', 'percentage')
    def _compute_earnings_nrr(self):
        for rec in self:
            nrr = rec.order_id.dealsheet_id.nrr
            earnings_nrr = (nrr * rec.percentage) / 100
            rec.earnings_nrr = earnings_nrr * rec.rate

    @api.depends('rate', 'order_id.dealsheet_id.mrr', 'percentage')
    def _compute_earnings_mrr(self):
        for rec in self:
            mrr = rec.order_id.dealsheet_id.mrr
            earnings_mrr = (mrr * rec.percentage) / 100
            rec.earnings_mrr = earnings_mrr * rec.rate

    @api.depends('margin_nrr', 'nrm_factor', 'manager_adjustment_nrr')
    def _compute_commission_nrr(self):
        for rec in self:
            rec.commission_nrr = (rec.margin_nrr * rec.nrm_factor
                                  * rec.manager_adjustment_nrr)

    @api.depends('earnings_mrr', 'duration_factor', 'mrr_factor',
                 'renewal_factor', 'manager_adjustment_mrr')
    def _compute_commission_mrr(self):
        for rec in self:
            rec.commission_mrr = (rec.earnings_mrr * rec.duration_factor
                                  * rec.mrr_factor * rec.renewal_factor
                                  * rec.manager_adjustment_mrr)

    @api.depends('commission_mrr', 'commission_nrr')
    def _compute_commission(self):
        for rec in self:
            rec.commission = rec.commission_mrr + rec.commission_nrr

    @api.depends('confirmation_date', 'user_id')
    def _compute_quarter_id(self):
        for rec in self:
            if rec.confirmation_date and rec.percentage and rec.user_id:
                rec.quarter_id = rec.get_or_create_quarter()

    def get_or_create_quarter(self):
        quarter_id = self.quarter_id.search([
            ('user_id', '=', self.user_id.id),
            ('year', '=', self.year),
            ('name', '=', self.quarter),
        ])
        if not quarter_id:
            quarter_id = self.quarter_id.sudo().create({
                'name': self.quarter,
                'user_id': self.user_id.id,
                'year': self.year,
                'target_id': self.get_target()
            })
        return quarter_id.id

    def get_target(self):
        return self.env['sale.target'].search([
            ('user_id', '=', self.user_id.id),
            ('year', '=', self.year)
        ]).id

    @api.depends('order_currency_id', 'currency_id', 'confirmation_date')
    def _compute_exchange_rate_id(self):
        for rec in self:
            if not rec.confirmation_date:
                continue
            confirmation_date = fields.Date.from_string(
                rec.confirmation_date).replace(day=1)
            confirmation_date_str = fields.Date.to_string(confirmation_date)
            rec.exchange_rate_id = rec.exchange_rate_id.search([
                ('company_id.currency_id', '=', rec.order_currency_id.id),
                ('currency_id', '=', rec.currency_id.id),
                ('name', '=', confirmation_date_str)
            ], limit=1).id

    @api.depends('exchange_rate_id.rate')
    def _compute_rate(self):
        for rec in self:
            if rec.exchange_rate_id:
                rec.rate = rec.exchange_rate_id.rate
            else:
                rec.rate = 1
