# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import fields, models, api


class ForecastMonth(models.Model):
    _name = "forecast.month"
    _description = "Forecast month"
    _rec_name = "total"
    _order = 'month'

    month = fields.Selection(
        selection=[(1, 'January'),
                   (2, 'February'),
                   (3, 'March'),
                   (4, 'April'),
                   (5, 'May'),
                   (6, 'July'),
                   (7, 'June'),
                   (8, 'August'),
                   (9, 'September'),
                   (10, 'October'),
                   (11, 'November'),
                   (12, 'December'),
                   ],
        required=True,
    )
    line_id = fields.Many2one(
        string='Line',
        comodel_name='forecast.line',
        ondelete='cascade',
        required=True,
    )
    type = fields.Selection(
        string='Type',
        related='line_id.type',
        readonly=True,
        store=True
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='line_id.report_id.currency_id',
        readonly=True,
    )
    report_id = fields.Many2one(
        string='Report',
        related='line_id.report_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        string='Company',
        related='report_id.company_id',
        readonly=True,
    )
    start_date = fields.Date(
        string='Start Date',
        compute='_compute_start_date',
        store=True,
    )
    source_currency_id = fields.Many2one(
        string='Source Currency',
        related='line_id.currency_id',
    )
    exchange_rate_id = fields.Many2one(
        string='Exchange Rate',
        comodel_name='res.currency.rate',
        compute='_compute_exchange_rate',
        store=True,
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='source_currency_id',
    )
    amount_converted = fields.Monetary(
        string='Amount converted',
        compute='_compute_amount_converted',
        store=True,
    )
    delta = fields.Monetary(
        string='Delta',
    )
    total = fields.Monetary(
        string='Total',
        inverse='_set_total',
        compute='_get_total',
        store=True
    )
    conversion_error = fields.Boolean(
        string='Is not correctly converted',
        compute='_compute_conversion_error',
        store=True
    )
    subs_start_date = fields.Date(
        string='Subscription Start Date',
    )
    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner'
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product'
    )
    categ_id = fields.Many2one(
        string='Category',
        related='product_id.categ_id'
    )
    is_locked = fields.Boolean(
        string='Is locked',
        compute='_compute_lock',
        store=True
    )

    @api.depends('report_id.year', 'month')
    def _compute_start_date(self):
        for record in self:
            record.update({
                'start_date': datetime(record.report_id.year, record.month, 1)
            })

    @api.depends('currency_id', 'source_currency_id', 'month',
                 'report_id.year')
    def _compute_exchange_rate(self):
        for record in self:
            rate = self.env['res.currency.rate']
            if record.start_date < fields.Date.today():
                exchange_rate_id = rate.search([
                    ('company_id', '=', record.report_id.company_id.id),
                    ('currency_id', '=', record.source_currency_id.id),
                    ('name', '=', record.start_date)
                ], limit=1)
            else:
                exchange_rate_id = rate.search([
                    ('company_id', '=', record.report_id.company_id.id),
                    ('currency_id', '=', record.source_currency_id.id),
                ], order='name desc', limit=1)
            if not exchange_rate_id:
                continue
            record.update({
                'exchange_rate_id': exchange_rate_id.id
            })

    @api.depends('amount', 'exchange_rate_id.rate')
    def _compute_amount_converted(self):
        for rec in self:
            if rec.currency_id == rec.source_currency_id:
                rec.update({
                    'amount_converted': rec.amount
                })
                continue
            if not rec.exchange_rate_id:
                rec.update({
                    'amount_converted': 0,
                })
                continue
            rec.update({
                'amount_converted': rec.amount / rec.exchange_rate_id.rate
            })

    @api.depends('amount', 'amount_converted')
    def _compute_conversion_error(self):
        for rec in self:
            if rec.amount and not rec.amount_converted:
                rec.update({
                    'conversion_error': True,
                })

    def _set_total(self):
        for record in self:
            record.update({
                'delta': record.total - record.amount_converted
            })

    @api.depends('delta', 'amount_converted')
    def _get_total(self):
        for record in self:
            record.update({
                'total': record.delta + record.amount_converted
            })

    @api.depends('report_id.lock_month')
    def _compute_lock(self):
        for rec in self:
            rec.update({
                'is_locked': rec.month <= rec.report_id.lock_month
            })
