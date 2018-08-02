# -*- coding: utf-8 -*-
# Copyright 2018 BSO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class BSODashboardGraphFilter(models.Model):
    _name = 'bso.dashboard.graph.filter'
    _order = 'graph_id ASC, sequence ASC, id ASC'
    _rec_name = 'domain'

    graph_id = fields.Many2one(
        string='Graph',
        comodel_name='bso.dashboard.graph',
        readonly=True
    )
    model_id = fields.Many2one(
        string='Model',
        related='graph_id.model_id',
        readonly=True
    )
    model_field_ids = fields.Many2many(
        string='Model Fields',
        related='graph_id.model_field_ids',
        readonly=True
    )
    field_id = fields.Many2one(
        string='Field',
        comodel_name='ir.model.fields'
    )
    field_ttype = fields.Selection(
        string='Field Type',
        related='field_id.ttype',
        readonly=True
    )
    condition = fields.Selection(
        string='Condition',
        selection=[
            ('=', 'Equal'),
            ('!=', 'Different'),
            ('<', 'Inferior'),
            ('>', 'Superior'),
            ('<=', 'Inferior or Equal'),
            ('>=', 'Superior or Equal'),
            ('=?', 'Conditional Equal'),
            ('ilike', 'Contains'),
            ('not ilike', 'Excludes'),
            ('in', 'In'),
            ('not in', 'Not In'),
            ('child_of', 'Child of')
        ]
    )
    value = fields.Char(
        string='Value'
    )
    value_dynamic_input = fields.Char(
        string='or Eval',
        help='Available variables: env, date, datetime'
    )
    value_dynamic = fields.Char(
        string='or Eval',
        compute='compute_value_dynamic',
        store=True
    )
    date_picker = fields.Datetime(
        string='Date'
    )
    datetime_picker = fields.Datetime(
        string='Datetime'
    )
    date_dynamic = fields.Selection(
        string='or Dynamic',
        selection=[
            ('<eval>date.today()[:-2]+"01"</eval>', 'This Month'),
            ('<eval>date.today()[:-5]+"01-01"</eval>', 'This Year')
        ]
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    domain = fields.Char(
        string='Domain',
        required=True
    )

    @api.depends('value_dynamic_input')
    def compute_value_dynamic(self):
        for rec in self:
            if not rec.value_dynamic_input:
                continue
            rec.value_dynamic = "<eval>%s</eval>" % rec.value_dynamic_input

    @api.onchange('field_id', 'condition', 'value', 'value_dynamic',
                  'date_picker', 'datetime_picker', 'date_dynamic')
    def onchange_inputs(self):
        field_str = self.field_id.name or 'field'
        condition_str = self.condition or 'condition'
        value_str = self.value or self.value_dynamic or self.date_picker \
                    or self.datetime_picker or self.date_dynamic or 'value'
        domain = '["%s", "%s", "%s"]' % (field_str, condition_str, value_str)
        self.domain = domain
