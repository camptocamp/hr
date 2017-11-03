# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    RENEWAL_DELTA_MAP = {
        'month': 1,
        'quarter': 3,
        'semester': 6,
    }

    duration = fields.Integer()
    recurring_total = fields.Monetary(string='Monthly Total')
    period_total = fields.Monetary(
        string='Period Total',
        compute='_compute_period_total',
        readonly=True,
    )

    automatic_renewal = fields.Selection(
        [('none', 'None'),
         ('same_dur', 'Same Duration'),
         ('month', 'Month'),
         ('quarter', 'Quarter'),
         ('semester', 'Semester')]
    )
    customer_prior_notice = fields.Integer(
        string='Customer Prior Notice (months)',
        help='Number of month before end of contract'
    )
    date_cancelled = fields.Date(
        string='Date Cancelled'
    )

    @api.depends('recurring_total', 'recurring_interval')
    def _compute_period_total(self):
        for sub in self:
            sub.period_total = sub.recurring_total * sub.recurring_interval

    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(SaleSubscription, self)._prepare_invoice_line(
            line=line, fiscal_position=fiscal_position)
        if self.recurring_interval:
            res['quantity'] = self.recurring_interval * res['quantity']
        return res

    @api.onchange('date_start',
                  'duration',
                  'customer_prior_notice',
                  'date_cancelled')
    def onchange_date_duration(self):
        if not self.date_cancelled:
            if self.date_start and self.duration:
                self.date = (fields.Date.from_string(self.date_start) +
                             relativedelta(months=self.duration))
        else:
            if self.date:
                date_prior_notice = (
                    fields.Date.from_string(self.date_cancelled) +
                    relativedelta(months=self.customer_prior_notice))
                if date_prior_notice >= fields.Date.from_string(self.date):
                    self.date = date_prior_notice

    @api.onchange('template_id')
    def on_change_template(self):
        if self.template_id:
            self.automatic_renewal = self.template_id.automatic_renewal
            self.customer_prior_notice = self.template_id.customer_prior_notice
        super(SaleSubscription, self).on_change_template()

    def _subscription_make_pending(self, next_month):
        """Set to pending if date is in less than a month and no auto renewal
        """
        domain_pending = [('date', '<', next_month),
                          ('state', '=', 'open'),
                          ('automatic_renewal', '=', 'none')]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.write({'state': 'pending'})
        return subscriptions_pending

    def _subscription_make_close(self, today):
        """Set to close if data is passed and no auto renewal"""
        domain_close = [('date', '<', today),
                        ('state', 'in', ['pending', 'open']),
                        ('automatic_renewal', '=', 'none')]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.write({'state': 'close'})
        return subscriptions_close

    def _subscription_make_auto_open(self, today):
        """ Subscription auto renewal"""
        domain_open = [('date', '<', today),
                       ('state', 'in', ['pending', 'open']),
                       ('automatic_renewal', '!=', 'none')]
        subscriptions = self.search(domain_open)

        for sub in subscriptions:
            if sub.automatic_renewal == 'same_dur':
                delta = relativedelta(fields.Date.from_string(sub.date),
                                      fields.Date.from_string(sub.date_start))
            else:
                months = self.RENEWAL_DELTA_MAP.get(sub.automatic_renewal)
                delta = relativedelta(months=months)
            new_date = fields.Date.from_string(sub.date) + delta
            sub.write({'date': new_date})
        return subscriptions

    @api.model
    def cron_account_analytic_account(self):
        """Taking back original method from `sale_contract` with modifications
        in order to have original cron working only on non automatic_renewal.
        The old method has been splitted in two functions
        """
        today = fields.Date.today()
        next_month = fields.Date.to_string(
            fields.Date.from_string(today) + relativedelta(months=1))

        subscriptions_pending = self._subscription_make_pending(next_month)
        subscriptions_close = self._subscription_make_close(today)
        subscriptions_open = self._subscription_make_auto_open(today)

        return dict(open=subscriptions_open.ids,
                    pending=subscriptions_pending.ids,
                    closed=subscriptions_close.ids)
