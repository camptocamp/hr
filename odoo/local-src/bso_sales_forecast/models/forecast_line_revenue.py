# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ForecastLineRevenue(models.Model):
    _name = "forecast.line.revenue"
    _description = "Forecast Line Revenue"

    line_id = fields.Many2one(
        string='Forecast Line',
        comodel_name='forecast.line',
        delegate=True,
        ondelete='cascade',
        required=True,
    )
    subscription_line_id = fields.Many2one(
        string='Subscription Line',
        comodel_name='sale.subscription.line',
    )
    price_subtotal = fields.Float(
        string='Price Subtotal',
        related="subscription_line_id.price_subtotal",
        readonly=True,
    )
    subscription_id = fields.Many2one(
        string='Subscription',
        related="subscription_line_id.analytic_account_id",
        readonly=True,
    )
    # currency_id = fields.Many2one(
    #     string='Currency',
    #     related='subscription_id.pricelist_id.currency_id',
    #     store=True
    # )
    product_id = fields.Many2one(
        string='Product',
        related='subscription_line_id.product_id',
        readonly=True,
    )
    categ_id = fields.Many2one(
        string='Category',
        related='product_id.categ_id',
        readonly=True,
        store=True,
    )
    partner_id = fields.Many2one(
        string='Customer',
        related='subscription_id.partner_id',
        readonly=True,
    )
    subs_start_date = fields.Date(
        string='Subscription Start Date',
        related='subscription_id.date_start',
        readonly=True,
    )
    subs_end_date = fields.Date(
        string='Subscription End Date',
        compute='_compute_subs_end_date',
        store='True',
    )
    automatic_renewal = fields.Selection(
        string='Automatic Renewel',
        related='subscription_id.automatic_renewal',
        readonly=True
    )
    form_id = fields.Many2one(
        string='Open',
        comodel_name='forecast.line.revenue',
        readonly=True,
    )

    @api.model
    def create(self, values):
        subscription_line = self.subscription_line_id.browse(
            values['subscription_line_id'])
        subscription = subscription_line.analytic_account_id
        report = self.env['forecast.report'].browse(values['report_id'])

        subs_start_date = subscription.date_start
        subs_end_dt = self._get_subs_end_date(subscription, report)
        amount = subscription_line.price_subtotal
        values['currency_id'] = subscription.pricelist_id.currency_id.id
        values['type'] = self.line_id.get_type(subscription, subscription_line,
                                               subs_start_date, report,
                                               suffix='r')
        month_amounts = self.line_id.get_month_amounts(subs_start_date,
                                                       subs_end_dt, report,
                                                       amount)
        values.update(month_amounts)
        rec = super(ForecastLineRevenue, self).create(values)
        rec.form_id = rec.id
        return rec

    @api.depends('subscription_id', 'report_id')
    def _compute_subs_end_date(self):
        for rec in self:
            subs_end_date = rec._get_subs_end_date(rec.subscription_id,
                                                   rec.report_id)
            rec.update({'subs_end_date': subs_end_date})

    @api.model
    def _get_subs_end_date(self, subscription_id, report_id):
        if subscription_id.date \
                and subscription_id.automatic_renewal in (False, 'none'):
            subs_end_date = subscription_id.date
        else:
            subs_end_date = report_id.end_date
        return subs_end_date
