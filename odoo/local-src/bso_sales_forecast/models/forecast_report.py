# -*- coding: utf-8 -*-
import calendar
import logging
from datetime import datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ForecastReport(models.Model):
    _name = "forecast.report"
    _description = "Forecast report"

    _sql_constraints = [
        ('name_unique', 'unique (name)',
         "This report is already created."),
    ]

    name = fields.Char(
        string='Report',
        compute='compute_name',
        store=True
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        related='company_id.currency_id',
        readonly=True,
    )
    year = fields.Integer(
        string='Year',
        readonly=True,
    )
    start_date = fields.Date(
        string='Start date',
        readonly=True,
    )
    end_date = fields.Date(
        string='End date',
        readonly=True,
    )
    refresh_date = fields.Date(
        string='Refresh date',
        readonly=True,
    )
    revenue_lines = fields.One2many(
        string='Report Revenues',
        comodel_name='forecast.line.revenue',
        inverse_name='report_id',
    )
    mis_report_id = fields.Many2one(
        string='MIS Report',
        comodel_name='mis.report.instance',
    )

    cost_lines = fields.One2many(
        string='Report Cost Lines',
        comodel_name='forecast.line.cost',
        inverse_name='report_id',
    )
    invoice_lines = fields.One2many(
        string='Report Invoice Lines',
        comodel_name='forecast.line.invoice',
        inverse_name='report_id',
    )
    lock_date = fields.Date(
        string='Lock date',
    )
    lock_month = fields.Selection(
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
        compute='compute_lock_month',
        store=True,
    )

    @api.model
    def _get_current_year(self):
        return datetime.today().year

    @api.depends('company_id')
    def compute_name(self):
        for rec in self:
            rec.update({
                'name': "%s %s" % (rec.company_id.name, datetime.today().year)
            })

    @api.depends('year')
    def compute_start_date(self):
        for rec in self:
            rec.update({
                'start_date': datetime(rec.year, 1, 1)
            })

    @api.depends('year')
    def compute_end_date(self):
        for rec in self:
            rec.update({
                'end_date': datetime(rec.year, 12, 31)
            })

    @api.depends('lock_date')
    def compute_lock_month(self):
        for rec in self:
            if rec.lock_date:
                rec.lock_month = fields.Date.from_string(rec.lock_date).month

    @api.model
    def create(self, values):
        year = values.get('year') or datetime.today().year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        values.update({
            'year': year,
            'start_date': start_date,
            'end_date': end_date,
            'refresh_date': datetime.today(),
        })
        report = super(ForecastReport, self).create(values)
        report.get_revenue_lines(values['company_id'])
        report.get_cost_lines(values['company_id'])
        report.get_invoice_lines(values['company_id'], start_date, end_date)
        return report

    def get_revenue_lines(self, company_id):
        subscription_line_ids = self.get_subscription_lines(company_id)
        for line_id in subscription_line_ids:
            self.env['forecast.line.revenue'].create(
                {'subscription_line_id': line_id,
                 'report_id': self.id})
        return

    def get_subscription_lines(self, company_id):
        return self.env['sale.subscription.line'].search([
            ('analytic_account_id.state', 'in', ['open', 'paid']),
            ('analytic_account_id.company_id', '=', company_id),
            '|',
            ('analytic_account_id.automatic_renewal', 'not in',
             [False, 'none']),
            ('analytic_account_id.date', '>=', datetime.today()),
        ]).ids

    def get_cost_lines(self, company_id):
        purchase_lines = self.get_purchase_lines(company_id)
        for line_id in purchase_lines:
            self.env['forecast.line.cost'].create(
                {'purchase_order_line_id': line_id,
                 'report_id': self.id})
        return

    def get_purchase_lines(self, company_id):
        return self.env['purchase.order.line'].search([
            ('order_id.state', 'in', ['purchase', 'done']),
            ('order_id.company_id', '=', company_id),
            ('product_id.recurring_invoice', '=', True),
            '|',
            ('order_id.continue_after_end', '!=', False),
            ('order_id.subscr_date_end', '>=', datetime.today()),
        ]).ids

    def get_invoice_lines(self, company_id, start_date, end_date):
        account_invoice_lines = self.get_account_invoice_lines(company_id,
                                                               start_date,
                                                               end_date)
        for line_id in account_invoice_lines:
            self.env['forecast.line.invoice'].create(
                {'invoice_line_id': line_id,
                 'report_id': self.id})
        return

    def get_account_invoice_lines(self, company_id, start_date, end_date):
        return self.env['account.invoice.line'].search([
            ('invoice_id.state', 'in', ('open', 'paid')),
            ('invoice_id.company_id', '=', company_id),
            ('product_id.product_tmpl_id.recurring_invoice', '=', False),
            ('invoice_id.date_invoice', '<=', end_date),
            ('invoice_id.date_invoice', '>=', start_date),
        ]).ids

    @api.multi
    def open_telco_revenue_lines(self):
        self.ensure_one()
        return {
            "name": "Telco revenues",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.revenue",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_telco_r', 'telco_r', 'intercompany_telco_r']),
                       ],
        }

    @api.multi
    def open_telco_cost_lines(self):
        self.ensure_one()
        return {
            "name": "Telco costs",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.cost",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_telco_c', 'telco_c', 'intercompany_telco_c']),
                       ],
        }

    @api.multi
    def open_housing_revenue_lines(self):
        self.ensure_one()
        return {
            "name": "Housing revenues",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.revenue",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_housing_r', 'housing_r',
                         'intercompany_housing_r']),
                       ],
        }

    @api.multi
    def open_housing_cost_lines(self):
        self.ensure_one()
        return {
            "name": "Housing costs",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.cost",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_housing_c', 'housing_c',
                         'intercompany_housing_c']),
                       ],
        }

    @api.multi
    def open_managed_service_revenue_lines(self):
        self.ensure_one()
        return {
            "name": "Managed services revenues",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.revenue",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_managedservice_r', 'managedservice_r',
                         'intercompany_managedservice_r']),
                       ],
        }

    @api.multi
    def open_managed_service_cost_lines(self):
        self.ensure_one()
        return {
            "name": "Managed services costs",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.cost",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id},
            "domain": [('report_id', '=', self.id),
                       ('type', 'in',
                        ['n_managedservice_c', 'managedservice_c',
                         'intercompany_managedservice_c']),
                       ],
        }

    @api.multi
    def open_technical_team_lines(self):
        self.ensure_one()
        return {
            "name": "Technical Team lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'tech_team_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'tech_team_m')],
        }

    @api.multi
    def open_delivery_team_lines(self):
        self.ensure_one()
        return {
            "name": "Delivery Team lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'del_team_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'del_team_m')],
        }

    @api.multi
    def open_sales_department_lines(self):
        self.ensure_one()
        return {
            "name": "Sales Department lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'sales_dep_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'sales_dep_m')],
        }

    @api.multi
    def open_hr_lines(self):
        self.ensure_one()
        return {
            "name": "HR lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'hr_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'hr_m')],
        }

    @api.multi
    def open_communication_lines(self):
        self.ensure_one()
        return {
            "name": "Communication lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'communication_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'communication_m')],
        }

    @api.multi
    def open_finance_department_lines(self):
        self.ensure_one()
        return {
            "name": "Finance Department lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'finance_dep_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'finance_dep_m')],
        }

    @api.multi
    def open_marketing_lines(self):
        self.ensure_one()
        return {
            "name": "Marketing lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'marketing_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'marketing_m')],
        }

    @api.multi
    def open_other_costs_lines(self):
        self.ensure_one()
        return {
            "name": "Other Costs lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'other_costs_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'other_costs_m')],
        }

    @api.multi
    def open_telecom_lines(self):
        self.ensure_one()
        return {
            "name": "Telecom lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'telecom'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'telecom_m')],
        }

    @api.multi
    def open_lawyers_accountants_lines(self):
        self.ensure_one()
        return {
            "name": "Lawyers & Accountants lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'lawyers_accountants_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'lawyers_accountants_m')],
        }

    @api.multi
    def open_costs_non_invest_lines(self):
        self.ensure_one()
        return {
            "name": "Costs Non Invest lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'costs_non_invest_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'costs_non_invest_m')],
        }

    @api.multi
    def open_ga_inter_co_rebill_lines(self):
        self.ensure_one()
        return {
            "name": "G&A Inter Co Rebill",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'g_a_inter_co_rebill_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'g_a_inter_co_rebill_m')],
        }

    @api.multi
    def open_new_pop_amortization_lines(self):
        self.ensure_one()
        return {
            "name": "New Pop Amortization lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'new_pop_amortization_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'new_pop_amortization_m')],
        }

    @api.multi
    def open_leasing_backbone_lines(self):
        self.ensure_one()
        return {
            "name": "Leasing Backbone lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'leasing_backbone_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'leasing_backbone_m')],
        }

    @api.multi
    def open_accurals_bad_debts_lines(self):
        self.ensure_one()
        return {
            "name": "Accurals Bad Debts lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'accurals_bad_debts_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'accurals_bad_debts_m')],
        }

    @api.multi
    def open_foreign_exchanges_lines(self):
        self.ensure_one()
        return {
            "name": "Foreign Exchanges lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'foreign_exchanges_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'foreign_exchanges_m')],
        }

    @api.multi
    def open_clevel_lines(self):
        self.ensure_one()
        return {
            "name": "Clevel lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.manual",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        'default_type': 'clevel_m'},
            "domain": [('report_id', '=', self.id),
                       ('type', '=', 'clevel_m')],
        }

    @api.multi
    def open_invoice_lines(self):
        self.ensure_one()
        return {
            "name": "Invoice lines",
            "type": "ir.actions.act_window",
            "res_model": "forecast.line.invoice",
            "view_type": "form",
            "view_mode": "tree,form",
            "context": {'default_report_id': self.id,
                        # 'default_type': 'clevel_m'
                        },
            "domain": [('report_id', '=', self.id),
                       # ('type', '=', 'clevel_m')
                       ],
        }

    @api.model
    def generate_forecast_reports(self):
        bso_companies = self.env['res.company'].search([])
        for company in bso_companies:
            self.create({
                'company_id': company.id,
            })
            _logger.info('%s report created', company.name)

    @api.multi
    def preview(self):
        self.ensure_one()
        if not self.mis_report_id:
            template = self.env['mis.report'].search(
                [('name', '=', 'Sales Forecast Template')])
            mis_report_id = self._create_mis_report(template)
            self.write({'mis_report_id': mis_report_id})
        return self.mis_report_id.preview()

    @api.model
    def _create_mis_report(self, template):
        if not template:
            report_id = self._create_mis_template()
        else:
            report_id = template.id
        return self.mis_report_id.create({
            'name': self.name,
            'report_id': report_id,
            'year': self.year,
            'company_id': self.company_id.id,
            'comparison_mode': True,
            'period_ids': self._get_period_values(),
            'forecast_report_id': self.id,
        }).id

    @api.model
    def _create_mis_template(self):
        types = self.env['forecast.line'].type_selection()
        template_id = self.mis_report_id.report_id.create({
            'name': 'Sales Forecast Template',
            'query_ids': [(0, 0, self._get_query_value(t)) for t in types],
            'kpi_ids': [(0, 0, self._get_kpi_value(t)) for t in types],
        }).id
        return template_id

    def _get_query_value(self, type):
        key = type[0]
        return {
            'name': 'q_%s' % key,
            'row_model_id': self._get_row_model_id(suffix=key[-1]),
            'model_id': self._get_model_id(),
            'field_ids': [(6, 0, [self._get_field_ids('total')])],
            'aggregate': 'sum',
            'date_field': self._get_field_ids('start_date'),
            'domain': "[(\'type\',\'=\',\'%s\')]" % key,
        }

    @api.model
    def _get_kpi_value(self, type):
        key = type[0]
        value = type[1]
        return {
            'description': value,
            'type': 'num',
            'compare_method': 'pct',
            'name': key,
            'accumulation_method': 'sum',
            'expression': 'q_%s.total' % key
        }

    def _get_row_model_id(self, suffix):
        ref = 'bso_sales_forecast.model_forecast_line'
        if suffix == 'r':
            return self.env.ref('%s_revenue' % ref).id
        elif suffix == 'c':
            return self.env.ref('%s_cost' % ref).id
        elif suffix == 'i':
            return self.env.ref('%s_invoice' % ref).id
        else:
            return self.env.ref('%s_manual' % ref).id

    def _get_model_id(self):
        return self.env.ref('bso_sales_forecast.model_forecast_month').id

    def _get_field_ids(self, field_name):
        return self.env['ir.model.fields'].search([
            ('name', '=', field_name)
        ], limit=1).id

    @api.model
    def _get_period_values(self):
        period_values = []
        for month in range(1, 13):
            date_from = datetime(self.year, month, 1)
            last_day = calendar.monthrange(self.year, month)[1]
            period_value = {
                'name': date_from.strftime('%B'),
                'source': 'actuals',
                'manual_date_from': date_from,
                'manual_date_to': datetime(self.year, month, last_day),
            }
            period_values.append((0, 0, period_value))
        return period_values

    @api.multi
    def refresh(self):
        self.ensure_one()
        line_diffs = self._get_line_diffs()
        line_diffs.apply_changes()
        return True

    def _get_line_diffs(self):
        return self.env['forecast.line.diff'].search([
            '|',
            ('report_id', '=', self.id),
            '&',
            ('company_id', '=', self.company_id.id),
            ('line_id', '=', False)
        ])
