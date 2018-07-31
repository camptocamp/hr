# -*- coding: utf-8 -*-
# Copyright 2018 BSO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class BSODashboardGraphSettings(models.Model):
    _name = 'bso.dashboard.graph.settings'

    name = fields.Char(
        default='Graph Settings',
        readonly=True
    )
    graph_id = fields.Many2one(
        string='Graph',
        comodel_name='bso.dashboard.graph',
        ondelete='cascade',
        readonly=True,
        required=True
    )
    graph_type = fields.Selection(
        related='graph_id.graph_type',
        required=True,
        store=True
    )

    # BAR, LINE & PIE SETTINGS
    height = fields.Integer(
        string='Height',
        default=250
    )
    width = fields.Integer(
        string='Width',
        default=450
    )
    margin_left = fields.Integer(
        string='Margin Left',
        default=0
    )
    margin_right = fields.Integer(
        string='Margin Right',
        default=0
    )
    margin_top = fields.Integer(
        string='Margin Top',
        default=10
    )
    margin_bottom = fields.Integer(
        string='Margin Bottom',
        default=20
    )
    show_sum = fields.Boolean(
        string='Show Sum',
        default=True
    )

    # BAR & LINE SETTINGS
    show_x_axis = fields.Boolean(
        string='Show X Axis',
        default=True
    )
    show_y_axis = fields.Boolean(
        string='Show Y Axis',
        default=False
    )
    right_align_y_axis = fields.Boolean(
        string='Right Align Y Axis',
        default=False
    )

    # BAR SETTINGS
    show_values = fields.Boolean(
        string='Show Values',
        default=False
    )

    # LINE SETTINGS
    area = fields.Boolean(
        string='is Area',
        default=True
    )

    # PIE SETTINGS
    donut = fields.Boolean(
        string='is Donut',
        default=False
    )
    show_legend = fields.Boolean(
        string='Show Legend',
        default=True
    )
    legend_position = fields.Selection(
        string='Legend Position',
        selection=[
            ('top', 'Top'),
            ('right', 'Right')
        ],
        default='top'
    )
    show_labels = fields.Boolean(
        string='Show Labels',
        default=True
    )
    labels_outside = fields.Boolean(
        string='Labels Outside',
        default=False
    )
    label_type = fields.Selection(
        string='Label Type',
        selection=[
            ('key', 'Key'),
            ('value', 'Value'),
            ('percent', 'Percent')
        ]
    )
    label_sunbeam_layout = fields.Boolean(
        string='Label Sunbeam Layout',
        default=False
    )
