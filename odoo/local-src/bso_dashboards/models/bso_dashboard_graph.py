# -*- coding: utf-8 -*-
# Copyright 2018 BSO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json
from collections import OrderedDict, defaultdict

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory


class BSODashboardGraph(models.Model):
    _name = 'bso.dashboard.graph'
    _order = 'dashboard_id ASC, sequence ASC, id ASC'

    def _default_dashboard_id(self):
        return self.env.context.get('active_id', False)

    dashboard_id = fields.Many2one(
        string='Dashboard',
        comodel_name='bso.dashboard',
        default=lambda self: self._default_dashboard_id(),
        ondelete='cascade',
        readonly=True,
        required=True
    )
    model_id = fields.Many2one(
        string='Model',
        comodel_name='ir.model',
        required=True
    )
    model_field_ids = fields.Many2many(
        string='Model Fields',
        comodel_name='ir.model.fields',
        compute='compute_model_field_ids',
        store=True
    )
    measure_id = fields.Many2one(
        string='Measure',
        comodel_name='ir.model.fields',
        required=True
    )
    measure_ttype = fields.Selection(
        string='Measure Type',
        related='measure_id.ttype',
        readonly=True
    )
    measure_currency_id = fields.Many2one(
        string='Currency Field',
        comodel_name='ir.model.fields'
    )
    measure_consolidate_id = fields.Many2one(
        string='Consolidate In',
        comodel_name='res.currency'
    )
    measure_key = fields.Char(
        string='Measure Key',
        compute='compute_measure_key',
        store=True
    )
    groupby_id = fields.Many2one(
        string='Group By',
        comodel_name='ir.model.fields',
        required=True
    )
    groupby_ttype = fields.Selection(
        string='Groupby Type',
        related='groupby_id.ttype',
        readonly=True
    )
    groupby_interval = fields.Selection(
        string='Interval',
        selection=[
            ('day', 'Day'),
            ('week', 'Week'),
            ('month', 'Month'),
            ('quarter', 'Quarter'),
            ('year', 'Year')
        ]
    )
    groupby_key = fields.Char(
        string='Groupby Key',
        compute='compute_groupby_key',
        store=True
    )
    filter_ids = fields.One2many(
        string='Filters',
        comodel_name='bso.dashboard.graph.filter',
        inverse_name='graph_id'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    name = fields.Char(
        string='Title',
        required=True
    )
    graph_type = fields.Selection(
        string='Type',
        selection=[
            ('bar', 'Bar'),
            ('line', 'Line'),
            ('pie', 'Pie')
        ],
        required=True
    )
    settings_id = fields.Many2one(
        string='Settings',
        comodel_name='bso.dashboard.graph.settings',
        readonly=True
    )
    graph = fields.Text(
        string='Graph',
        compute='compute_graph'
    )

    @api.model
    def create(self, values):
        graph = super(BSODashboardGraph, self).create(values)
        settings = graph.settings_id.create({
            'graph_id': graph.id
        })
        graph.write({
            'settings_id': settings.id
        })
        return graph

    @api.depends('model_id.field_id')
    def compute_model_field_ids(self):
        for rec in self:
            if not rec.model_id:
                continue
            valid_field_names = self.env[rec.model_id.model].fields_get_keys()
            valid_field_ids = self.env['ir.model.fields'].search([
                ('model_id', '=', rec.model_id.id),
                ('name', 'in', valid_field_names)
            ])
            rec.model_field_ids = valid_field_ids.ids

    @api.depends('measure_id')
    def compute_measure_key(self):
        for rec in self:
            if rec.measure_id.name == 'id':
                rec.measure_key = '__count'
            else:
                rec.measure_key = rec.measure_id.name

    @api.depends('groupby_id', 'groupby_interval')
    def compute_groupby_key(self):
        for rec in self:
            groupby_key = rec.groupby_id.name
            if rec.groupby_interval:
                groupby_key += ":" + rec.groupby_interval
            rec.groupby_key = groupby_key

    @api.depends('model_id', 'measure_key', 'groupby_key', 'settings_id',
                 'measure_currency_id', 'measure_consolidate_id', 'filter_ids')
    def compute_graph(self):
        for rec in self:
            if not all((rec.model_id, rec.measure_key, rec.groupby_key,
                        rec.settings_id)):
                continue
            data = rec.get_graph_data()
            rec.graph = json.dumps({
                'data': rec.get_graph_format(data),
                'settings': rec.settings_id.read()[0]
            })

    def get_graph_data(self):
        return self.env[self.model_id.model].sudo().read_group(
            domain=self.get_search_domain(),
            fields=self.get_search_fields(),
            groupby=self.get_search_groupby(),
            offset=0,
            limit=None,
            orderby=self.groupby_id.name,
            lazy=False
        )

    def get_search_domain(self):
        domain = []
        for fltr in self.filter_ids:
            domain_evaluated = self._domain_eval(fltr.domain)
            domain.append(json.loads(domain_evaluated))
        return domain

    def _domain_eval(self, domain):
        start_tag, end_tag = "<eval>", "</eval>"
        start_idx, end_idx = domain.find(start_tag), domain.find(end_tag)
        if -1 in (start_idx, end_idx):
            return domain
        eval_tag = domain[start_idx:end_idx + len(end_tag)]
        eval_cmd = eval_tag[len(start_tag):-len(end_tag)]
        eval_val = safe_eval(eval_cmd, dict(env=self.env,
                                            date=fields.Date,
                                            datetime=fields.Datetime))
        return domain.replace(eval_tag, str(eval_val))

    def get_search_fields(self):
        fields = [self.measure_id.name, self.groupby_id.name]
        if self.measure_currency_id and self.measure_consolidate_id:
            fields.append(self.measure_currency_id.name)
        return fields

    def get_search_groupby(self):
        groupby = [self.groupby_key]
        if self.measure_currency_id and self.measure_consolidate_id:
            groupby.append(self.measure_currency_id.name)
        return groupby

    def get_graph_format(self, data):
        if not data:
            return
        if self.measure_currency_id and self.measure_consolidate_id:
            data = self._consolidate(data)
        if self.graph_type == 'bar':
            return self._graph_format_bar(data)
        if self.graph_type == 'line':
            return self._graph_format_line(data)
        if self.graph_type == 'pie':
            return self._graph_format_pie(data)

    def _consolidate(self, data):
        consolidated = OrderedDefaultDict(lambda: 0)
        for d in data:
            amount = d[self.measure_key]
            currency = d[self.measure_currency_id.name]
            converted = self._convert(amount, currency)
            consolidated[d[self.groupby_key]] += converted
        return [{self.measure_key: measure,
                 self.groupby_key: groupby}
                for groupby, measure in consolidated.iteritems()]

    def _convert(self, from_amount, from_currency):
        from_currency_id = self._get_value_id(from_currency)
        if from_currency_id:
            currency = self._get_res('res.currency', from_currency_id)
            if currency:
                return currency.compute(
                    from_amount=from_amount,
                    to_currency=self.measure_consolidate_id
                )
        return from_amount  # Fallback

    def _graph_format_bar(self, data):
        bar_data = [{'value': d[self.measure_key],
                     'label': self._get_value_name(d[self.groupby_key])}
                    for d in data]
        return [{'values': bar_data}]

    def _graph_format_line(self, data):
        line_data = [{'y': d[self.measure_key],
                      'x': self._get_value_name(d[self.groupby_key]),
                      'name': self._get_value_name(d[self.groupby_key])}
                     for d in data]
        return [{'values': line_data}]

    def _graph_format_pie(self, data):
        pie_data = [{'value': d[self.measure_key],
                     'key': self._get_value_name(d[self.groupby_key])}
                    for d in data]
        return pie_data

    def _get_res(self, res_model, res_id):
        return self.env[res_model].search([
            ('id', '=', res_id)
        ], limit=1)

    def _get_value_id(self, value):
        if isinstance(value, tuple):
            return value[0]
        return value

    def _get_value_name(self, value):
        if isinstance(value, tuple):
            return value[1]
        return value

    @api.constrains('model_id', 'measure_key', 'groupby_key', 'filter_ids')
    def validate_graph_data(self):
        self.get_graph_data()

    @api.multi
    def action_open_dashboard_graph(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "bso.dashboard.graph",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
        }

    @api.multi
    def action_open_dashboard_graph_settings(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "bso.dashboard.graph.settings",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.settings_id.id,
        }
