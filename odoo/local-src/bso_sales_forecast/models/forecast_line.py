# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


class ForecastLine(models.Model):
    _name = "forecast.line"
    _inherit = "mail.thread"

    name = fields.Char(
        default="Open",
        readonly=True,
    )
    report_id = fields.Many2one(
        string='Forecast Report',
        comodel_name='forecast.report',
        ondelete='cascade',
        required=True,
    )
    company_id = fields.Many2one(
        string='Company',
        related='report_id.company_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        string='Report Currency',
        comodel_name='res.currency',
        required=True,
    )
    months = fields.One2many(
        string='Months',
        comodel_name='forecast.month',
        inverse_name='line_id',
        readonly=True,
    )
    jan_id = fields.Many2one(
        string='January',
        comodel_name='forecast.month',
        readonly=True,
    )
    feb_id = fields.Many2one(
        string='February',
        comodel_name='forecast.month',
        readonly=True,
    )
    mar_id = fields.Many2one(
        string='March',
        comodel_name='forecast.month',
        readonly=True,
    )
    apr_id = fields.Many2one(
        string='April',
        comodel_name='forecast.month',
        readonly=True,
    )
    may_id = fields.Many2one(
        string='May',
        comodel_name='forecast.month',
        readonly=True,
    )
    jun_id = fields.Many2one(
        string='June',
        comodel_name='forecast.month',
        readonly=True,
    )
    jul_id = fields.Many2one(
        string='July',
        comodel_name='forecast.month',
        readonly=True,
    )
    aug_id = fields.Many2one(
        string='August',
        comodel_name='forecast.month',
        readonly=True,
    )
    sep_id = fields.Many2one(
        string='September',
        comodel_name='forecast.month',
        readonly=True,
    )
    oct_id = fields.Many2one(
        string='October',
        comodel_name='forecast.month',
        readonly=True,
    )
    nov_id = fields.Many2one(
        string='November',
        comodel_name='forecast.month',
        readonly=True,
    )
    dec_id = fields.Many2one(
        string='December',
        comodel_name='forecast.month',
        readonly=True,
    )
    report_currency_id = fields.Many2one(
        string='Currency',
        related='report_id.currency_id',
        readonly=True,
    )
    jan = fields.Monetary(
        string='January',
        related='jan_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    feb = fields.Monetary(
        string='February',
        related='feb_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    mar = fields.Monetary(
        string='March',
        related='mar_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    apr = fields.Monetary(
        string='April',
        related='apr_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    may = fields.Monetary(
        string='May',
        related='may_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    jun = fields.Monetary(
        string='June',
        related='jun_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    jul = fields.Monetary(
        string='July',
        related='jul_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    aug = fields.Monetary(
        string='August',
        related='aug_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    sep = fields.Monetary(
        string='September',
        related='sep_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    oct = fields.Monetary(
        string='October',
        related='oct_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    nov = fields.Monetary(
        string='November',
        related='nov_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    dec = fields.Monetary(
        string='December',
        related='dec_id.total',
        track_visibility='onchange',
        currency_field='report_currency_id'
    )
    conversion_error = fields.Boolean(
        string='Is not correctly converted',
        compute='_compute_conversion_error',
        store=True
    )
    jan_locked = fields.Boolean(
        string='Is Jan locked',
        related='jan_id.is_locked',
    )
    feb_locked = fields.Boolean(
        string='Is Feb locked',
        related='feb_id.is_locked',
    )
    mar_locked = fields.Boolean(
        string='Is Mar locked',
        related='mar_id.is_locked',
    )
    apr_locked = fields.Boolean(
        string='Is Apr locked',
        related='apr_id.is_locked',
    )
    may_locked = fields.Boolean(
        string='Is May locked',
        related='may_id.is_locked',
    )
    jun_locked = fields.Boolean(
        string='Is June locked',
        related='jun_id.is_locked',
    )
    jul_locked = fields.Boolean(
        string='Is Jul locked',
        related='jul_id.is_locked',
    )
    aug_locked = fields.Boolean(
        string='Is Aug locked',
        related='aug_id.is_locked',
    )
    sep_locked = fields.Boolean(
        string='Is Sep locked',
        related='sep_id.is_locked',
    )
    oct_locked = fields.Boolean(
        string='Is Oct locked',
        related='oct_id.is_locked',
    )
    nov_locked = fields.Boolean(
        string='Is Nov locked',
        related='nov_id.is_locked',
    )
    dec_locked = fields.Boolean(
        string='Is Dec locked',
        related='dec_id.is_locked',
    )
    manually_updated = fields.Boolean(
        string='Is Manually updated',
    )
    type = fields.Selection(
        string='Type',
        selection='type_selection',
    )

    @api.model
    def create(self, values):
        if not values.get('report_id'):
            values['report_id'] = self.env.context.get('report_id')
        if not values.get('currency_id'):
            values['currency_id'] = self.report_id.browse(
                values['report_id']).currency_id.id
        values['months'] = [(0, 0, {'month': idx + 1,
                                    'amount': values.get(m),
                                    }) for idx, m in enumerate(MONTHS)]
        rec = super(ForecastLine, self).create(values)
        rec.write({'%s_id' % MONTHS[m.month - 1]: m.id for m in rec.months})
        return rec

    @api.multi
    def write(self, values):
        record = super(ForecastLine, self).write(values)
        for rec in self:
            if any(month in values for month in MONTHS):
                rec.manually_updated = any(rec.months.mapped('delta'))
        return record

    @api.model
    def get_month_amounts(self, sub_start_dt, sub_end_dt, report, amount):
        start_dt = report.start_date
        end_dt = report.end_date
        start_m = self.get_max_start_month(sub_start_dt, start_dt)
        end_m = self.get_min_end_month(sub_end_dt, end_dt)
        return {m: amount for m in MONTHS[start_m - 1:end_m]}

    @api.model
    def get_max_start_month(self, subs_start_date, start_date):
        max_start_date = max(subs_start_date, start_date)
        max_start_dt = fields.Datetime.from_string(max_start_date)
        return max_start_dt.month

    @api.model
    def get_min_end_month(self, subs_end_date, end_date):
        min_end_date = min(subs_end_date, end_date)
        min_end_dt = fields.Datetime.from_string(min_end_date)
        return min_end_dt.month

    @api.depends('months.conversion_error')
    def _compute_conversion_error(self):
        for rec in self:
            if any(rec.months.mapped('conversion_error')):
                rec.update({
                    'conversion_error': True,
                })

    @api.model
    def get_type(self, item, item_line, date_start, report, suffix):
        category = item_line.product_id.categ_id
        category_key = self._get_category_key(category)
        if not category_key:
            return 'unknown_%s' % suffix
        if item.partner_id.bso_companies:
            return 'intercompany_%s_%s' % (category_key, suffix)
        if date_start > report.start_date:
            return 'n_%s_%s' % (category_key, suffix)
        return '%s_%s' % (category_key, suffix)

    @api.model
    def _get_category_key(self, categ):
        categories = ['telco', 'housing', 'managedservice', 'cloud']
        c = categ.name.lower().replace(' ', '')
        if c in categories:
            return c
        c = categ.parent_id.name.lower().replace(' ', '')
        if c in categories:
            return c

    @api.model
    def type_selection(self):
        return [('n_telco_r', 'NS -TELCO OPS'),
                ('telco_r', 'TELCO OPS'),
                ('intercompany_telco_r', 'INTERCOMPANY TELCO'),
                ('n_housing_r', 'NS - HOSTING & INFRA'),
                ('housing_r', 'HOSTING & INFRA'),
                ('intercompany_housing_r', 'INTERCOMPANY HOSTING'),
                ('n_cloud_r', 'NS - CLOUD'),
                ('cloud_r', 'CLOUD'),
                ('intercompany_cloud_r', 'INTERCOMPANY CLOUD'),
                ('n_managedservice_r', 'NS - MANAGED NETWORK & SERVICES'),
                ('managedservice_r', 'MANAGED NETWORK & SERVICES'),
                ('intercompany_managedservice_r', 'INTERCOMPANY MS'),
                ('n_telco_c', 'NC -TELCO OPS COSTS'),
                ('telco_c', 'TELCO OPS COSTS'),
                ('intercompany_telco_c', 'INTERCOMPANY TELCO COSTS'),
                ('n_housing_c', 'NC - HOSTING & INFRA COSTS'),
                ('housing_c', 'HOSTING & INFRA COSTS'),
                ('intercompany_housing_c', 'INTERCOMPANY HOSTING COSTS'),
                ('n_cloud_c', 'NC - CLOUD COSTS'),
                ('cloud_c', 'CLOUD COSTS'),
                ('intercompany_cloud_c', 'INTERCOMPANY CLOUD COSTS'),
                ('n_managedservice_c',
                 'NC - MANAGED NETWORK & SERVICES COSTS'),
                ('managedservice_c', 'MANAGED NETWORK & SERVICES COSTS'),
                ('intercompany_managedservice_c', 'INTERCOMPANY MS COSTS'),
                ('tech_team_m', 'TECHNICAL TEAM'),
                ('del_team_m', 'DELIVERY TEAM'),
                ('sales_dep_m', 'SALES DEPARTMENT'),
                ('hr_m', 'HR'),
                ('communication_m', 'COMMUNICATION'),
                ('finance_dep_m', 'FINANCE DEPARTMENT'),
                ('marketing_m', 'MARKETING COSTS AS PER BUDGET'),
                ('other_costs_m', 'OTHERS COSTS'),
                ('telecom_m', 'TELECOM'),
                ('lawyers_accountants_m', 'LAWYERS & ACCOUNTANTS'),
                ('costs_non_invest_m', 'COSTS NON INVEST'),
                ('g_a_inter_co_rebill_m', 'G& A INTER CO REBILL'),
                ('new_pop_amortization_m', 'NEW POP AMORTIZATION'),
                ('leasing_backbone_m', 'LEASING BACK BONE'),
                ('accurals_bad_debts_m',
                 'ACCRUALS BAD DEBTS - 1% of existing'),
                ('foreign_exchanges_m', 'FOREIGN EXCHANGES'),
                ('clevel_m', 'CLEVEL'),
                ('unknown_c', 'UNKNOWN COST'),
                ('unknown_r', 'UNKNOWN REVENUE'),
                ('unknown_i', 'UNKNOWN INVOICE'),
                ('services_r_i', 'SERVICES REVENUES ONE SHOT'),
                ('hardware_r_i', 'HARDWARE SALE'),
                ('intercompany_one_off_r_i', 'INTERCOMPANY ONE OFF REVENUES'),
                ('services_c_i', 'SERVICES COSTS ONE SHOT'),
                ('hardware_c_i', 'HARDWARE PURCHASES'),
                ('intercompany_one_off_c_i', 'INTERCOMPANY ONE OFF COSTS')
                ]
