# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    RENEWAL_DELTA_MAP = {
        'month': 1,
        'quarter': 3,
        'semester': 6,
    }

    duration = fields.Integer()
    recurring_total = fields.Monetary(
        compute='_compute_recurring_total',
        store=True, track_visibility='onchange',
        string='Monthly Total'
    )
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
    date_next_invoice_period_start = fields.Date(
        string="Start date of next invoice period",
        required=True
    )

    @api.depends('recurring_invoice_line_ids',
                 'recurring_invoice_line_ids.quantity',
                 'recurring_invoice_line_ids.price_subtotal')
    def _compute_recurring_total(self):
        super(SaleSubscription, self)._compute_recurring_total()

    @api.depends('recurring_total', 'recurring_interval')
    def _compute_period_total(self):
        for sub in self:
            sub.period_total = sub.recurring_total * sub.recurring_interval

    def _compute_invoice_count(self):
        super(SaleSubscription, self)._compute_invoice_count()
        orders = self.env['sale.order'].search_read(
            domain=[('subscription_id', 'in', self.ids)],
            fields=['name'],
        )
        order_names = [order['name'] for order in orders]
        invoice_line_data = self.env['account.invoice.line'].read_group(
            domain=[
                ('account_analytic_id', 'in', self.mapped(
                    'analytic_account_id',
                ).ids),
                ('invoice_id.name', 'in', self.mapped('code') + order_names),
                ('invoice_id.state', 'in', ['draft', 'open', 'paid'])
            ],
            fields=["account_analytic_id", "invoice_id"],
            groupby=["account_analytic_id", "invoice_id"],
            lazy=False
        )
        for sub in self:
            sub.invoice_count = len(filter(
                lambda d: d['account_analytic_id'][0] ==
                sub.analytic_account_id.id,
                invoice_line_data,
            ))

    @api.multi
    def action_subscription_invoice(self):
        res = super(SaleSubscription, self).action_subscription_invoice()
        analytic_ids = [sub.analytic_account_id.id for sub in self]
        orders = self.env['sale.order'].search_read(domain=[
            ('subscription_id', 'in', self.ids)
        ], fields=['name'])
        order_names = [order['name'] for order in orders]
        invoices = self.env['account.invoice'].search([
            ('invoice_line_ids.account_analytic_id', 'in', analytic_ids),
            ('name', 'in', self.mapped('code') + order_names)
        ])
        res['domain'] = [["id", "in", invoices.ids]]
        return res

    @api.model
    def _cron_recurring_create_invoice(self, nb_days=10):
        today = datetime.date.today()
        some_day_soon = today + datetime.timedelta(nb_days)
        exp_date = fields.Date.to_string(some_day_soon)
        subscriptions = self.search([('recurring_next_date', '<=', exp_date),
                                     ('state', '=', 'open')])
        return subscriptions._recurring_create_invoice(automatic=True)

    @api.returns('account.invoice')
    def _recurring_create_invoice(self, automatic=False):
        invoice_ids = super(SaleSubscription, self)._recurring_create_invoice(
            automatic=automatic)
        invoices = self.env["account.invoice"].browse(invoice_ids)
        # update 'date_next_invoice_period_start'
        periods = {'daily': 'days',
                   'weekly': 'weeks',
                   'monthly': 'months',
                   'yearly': 'years'}
        for sub in self:
            # Add origin to the invoice lines so
            # it will be propagated to their names
            invoices_to_update = invoices.filtered(
                lambda x: (x.mapped("invoice_line_ids.account_analytic_id") >=
                           sub.analytic_account_id)
            )
            orders = self.env['sale.order'].search_read(
                domain=[('subscription_id', '=', sub.id)],
                fields=['name'],
            )
            invoices_to_update.mapped("invoice_line_ids").write({
                'origin': u', '.join([order['name'] for order in orders]),
            })

            next_date = fields.Date.from_string(
                sub.date_next_invoice_period_start)
            rule, interval = sub.recurring_rule_type, sub.recurring_interval
            new_date = next_date + relativedelta(**{periods[rule]: interval})
            sub.write({'date_next_invoice_period_start': new_date})

        return invoice_ids

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        res = super(SaleSubscription, self)._prepare_invoice_line(
            line=line, fiscal_position=fiscal_position)
        if self.recurring_interval:
            res['quantity'] = self.recurring_interval * res['quantity']

        res.update(self.env['account.invoice.line'].update_dates(
            line.analytic_account_id.date_next_invoice_period_start,
            interval=self.recurring_interval))
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

    @api.multi
    def _prepare_invoice_data(self):
        self.ensure_one()
        res = super(SaleSubscription, self)._prepare_invoice_data()

        next_date = fields.Date.from_string(
            self.date_next_invoice_period_start)
        # Code copied from Odoo
        periods = {'daily': 'days',
                   'weekly': 'weeks',
                   'monthly': 'months',
                   'yearly': 'years'}
        end_date = next_date + relativedelta(
            **{periods[self.recurring_rule_type]: self.recurring_interval})
        # remove 1 day as normal people thinks in term of inclusive ranges.
        end_date = end_date - relativedelta(days=1)
        # DO NOT FORWARDPORT
        format_date = self.env['ir.qweb.field.date'].value_to_html
        # END code copied from Odoo

        res['comment'] = (
            _("This invoice covers the following period: %s - %s") %
            (format_date(fields.Date.to_string(next_date), {}),
             format_date(fields.Date.to_string(end_date), {}))
        )

        res['date'] = self.recurring_next_date
        res['date_invoice'] = self.recurring_next_date
        res['name'] = res.pop('origin', False)
        return res
