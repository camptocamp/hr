# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api

from forecast_line import MONTHS


class ForecastLineDiff(models.Model):
    _name = "forecast.line.diff"
    _description = "Forecast Line Diff"

    line_id = fields.Many2one(
        string='Forecast Line',
        comodel_name="forecast.line",
    )
    res_model = fields.Char(
        string='Resource Model',
        required=True,
    )
    res_id = fields.Integer(
        string='Resource ID',
    )
    action = fields.Selection(
        string='Action Type',
        required=True,
        selection=[
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete')
        ]
    )
    amount = fields.Float(
        string='Amount',
    )
    start_date = fields.Date(
        string='Start date'
    )
    end_date = fields.Date(
        string='End date'
    )
    auto_renewal = fields.Boolean(
        string='Automatic Renwal',
    )
    is_refund = fields.Boolean(
        string='Is refund',
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('open', 'Open'),
            ('close', 'Close'),
        ]
    )
    template_id = fields.Many2one(
        string='Subscription Template',
        comodel_name='sale.subscription.template',
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        compute='_get_company_id',
        store=True
    )
    report_id = fields.Many2one(
        string='Forecast Report',
        comodel_name='forecast.report',
        compute='_get_report_id',
        store=True,
        ondelete='cascade',
    )

    @api.depends('company_id')
    def _get_report_id(self):
        for rec in self:
            line = rec._get_line(rec.res_model, rec.res_id)
            if not line:
                report = self.env['forecast.report'].search([
                    ('company_id', '=', rec.company_id.id)
                ], limit=1)
                rec.update({'report_id': report.id})
                continue
            rec.update({'report_id': line.report_id.id})

    @api.depends('res_model', 'res_id')
    def _get_company_id(self):
        for rec in self:
            if not rec.line_id:
                company = self._get_company(rec.res_model, rec.res_id)
                rec.update({'company_id': company.id})
                continue
            rec.update({'company_id': rec.line_id.company_id.id})

    def _get_company(self, res_model, res_id):
        parent_field = self._get_forecast_line_dict(res_model).get(
            'fields_mapping').get('parent_field')
        line = self.env[res_model].browse(res_id)
        parent = getattr(line, parent_field)
        return parent.company_id

    def _get_line(self, res_model, res_id):
        forecast_line = self._get_forecast_line_dict(res_model).get(
            'forecast_line')
        forecast_model = forecast_line.get('model_name')
        original_line_field = forecast_line.get('original_line_field')
        line = self.env[forecast_model].search([
            (original_line_field, '=', res_id)
        ]).line_id
        return line

    @staticmethod
    def _get_forecast_line_dict(res_model):
        forecast_lines_dict = {
            'sale.subscription.line': {
                'forecast_line': {
                    'model_name': 'forecast.line.revenue',
                    'original_line_field': 'subscription_line_id',
                    'original_parent_field': 'subscription_id'
                },
                'fields_mapping': {
                    'end_date': 'date',
                    'auto_renewal': 'automatic_renewal',
                    'parent_field': 'analytic_account_id',
                    'amount': 'price_subtotal',
                    'template': 'template_id',
                },

            },
            'purchase.order.line': {
                'forecast_line': {
                    'model_name': 'forecast.line.cost',
                    'original_line_field': 'purchase_order_line_id',
                    'original_parent_field': 'purchase_order_id'
                },
                'fields_mapping': {
                    'end_date': 'subscr_date_end',
                    'auto_renewal': 'continue_after_end',
                    'parent_field': 'order_id',
                    'amount': 'price_subtotal',
                },
            },
            'account.invoice.line': {
                'forecast_line': {
                    'model_name': 'forecast.line.invoice',
                    'original_line_field': 'invoice_line_id',
                    'original_parent_field': 'invoice_id'
                },
                'fields_mapping': {
                    'end_date': 'date_invoice',
                    'parent_field': 'invoice_id',
                    'amount': 'price_subtotal',
                },

            },
        }
        return forecast_lines_dict.get(res_model)

    def log(self, res_model, res_id, action, values):
        line = self._get_line(res_model, res_id)
        line_diff = self.get_line_diff(res_model, res_id)
        if not line_diff:
            values.update({
                'line_id': line.id,
                'res_model': res_model,
                'res_id': res_id,
                'action': action})
            return self.create(values)
        if line_diff.action == 'create' and action == 'delete':
            return line_diff.unlink()
        if line_diff.action == 'update' and action == 'delete':
            return line_diff.write({'action': 'delete'})
        if line_diff.action == 'create' and action == 'update':
            values.update({'action': 'create'})
        line_diff.write(values)

    def get_line_diff(self, res_model, res_id):
        return self.search([
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
        ])

    def apply_changes(self):
        for rec in self:
            forecast_line_dict = self._get_forecast_line_dict(rec.res_model)
            forecast_line = forecast_line_dict.get('forecast_line')
            forecast_line_model = forecast_line.get('model_name')

            if not rec.line_id and rec.action == 'create':
                original_line_field = forecast_line.get('original_line_field')
                self.env[forecast_line_model].create({
                    original_line_field: rec.res_id,
                    'report_id': rec.report_id.id,
                })
                continue
            if not rec.line_id and rec.state == 'open':
                original_line_field = forecast_line.get('original_line_field')
                month_values = rec.get_month_values()
                self.env[forecast_line_model].create({
                    original_line_field: rec.res_id,
                    'report_id': rec.report_id.id,
                    'months': [(0, 0, {'month': idx + 1,
                                       'amount': month_values.get(m),
                                       }) for idx, m in enumerate(MONTHS)]
                })
                continue
            month_values = rec.get_month_values()
            current_month = fields.Datetime.from_string(rec.create_date).month
            for m in rec.line_id.months[current_month - 1:]:
                key = MONTHS[m.month - 1]
                if key in month_values:
                    m.write({'amount': month_values.get(key)})
                    continue
                m.write({'amount': 0})

            rec.unlink()

        return

    def get_month_values(self):
        if self.action == 'delete':
            current_month = datetime.today().month
            return {m: 0 for m in MONTHS[current_month:]}
        if self.is_refund:
            amount = - self.amount
        else:
            amount = self.amount
        if self.res_model == 'account.invoice.line':
            m = fields.Datetime.from_string(self.end_date).month
            return {MONTHS[m - 1]: amount}
        if self.auto_renewal:
            end_date = self.report_id.end_date
        else:
            end_date = self.end_date
        max_start_date = max(self.create_date, self.start_date)
        if 'arrears' in self.template_id.name:
            max_start_date = self._add_months_to_date(max_start_date)
            end_date = self._add_months_to_date(end_date)
        return self.line_id.get_month_amounts(max_start_date, end_date,
                                              self.report_id, amount)

    def _add_months_to_date(self, date_str):
        recurrence = self.template_id.recurring_interval
        date = fields.Datetime.from_string(date_str) + relativedelta(
            months=recurrence)
        return fields.Date.to_string(date)
