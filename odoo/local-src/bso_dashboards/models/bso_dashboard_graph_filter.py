# -*- coding: utf-8 -*-
# Copyright 2018 BSO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class BSODashboardGraphFilter(models.Model):
    _name = 'bso.dashboard.graph.filter'
    _order = 'graph_id ASC,sequence ASC,id ASC'
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
    date_picker = fields.Datetime(
        string='Date'
    )
    datetime_picker = fields.Datetime(
        string='Datetime'
    )
    date_dynamic = fields.Selection(
        string='or Dynamic',
        selection=[
            ('<exec>fields.Date.today()[:-2]+"01"</exec>', 'This Month'),
            ('<exec>fields.Date.today()[:-5]+"01-01"</exec>', 'This Year')
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

    @api.onchange('field_id', 'condition', 'value',
                  'date_picker', 'datetime_picker', 'date_dynamic')
    def onchange_inputs(self):
        field_str = self.field_id.name or 'field'
        condition_str = self.condition or 'condition'
        value_str = self.value or self.date_picker or self.datetime_picker
        value_str = value_str or self.date_dynamic or 'value'
        domain = '["%s", "%s", "%s"]' % (field_str, condition_str, value_str)
        self.update({
            'domain': domain
        })
