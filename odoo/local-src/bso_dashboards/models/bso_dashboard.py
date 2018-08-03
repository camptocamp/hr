# -*- coding: utf-8 -*-
# Copyright 2018 BSO
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api


class BSODashboard(models.Model):
    _name = 'bso.dashboard'

    def _default_group_id(self):
        return self.env.ref('bso_dashboards.group_dashboard_manager').id

    name = fields.Char(
        string='Title',
        required=True
    )
    group_id = fields.Many2one(
        string='Group',
        comodel_name='res.groups',
        default=lambda self: self._default_group_id(),
    )
    sum_graphs = fields.Integer(
        string="Graphs",
        compute="_compute_sum_graphs",
    )

    @api.multi
    def _compute_sum_graphs(self):
        graph_model = self.env['bso.dashboard.graph']
        for record in self:
            record.sum_graphs = graph_model.search_count([
                ('dashboard_id', '=', record.id)
            ])

    @api.multi
    def action_open_dashboard_graph(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "bso.dashboard.graph",
            "view_type": "form",
            "view_mode": "kanban,form",
            "usage": "menu",
            "domain": [
                ('dashboard_id', '=', self.id)]
        }

    @api.multi
    def action_open_dashboard(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "bso.dashboard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
        }
