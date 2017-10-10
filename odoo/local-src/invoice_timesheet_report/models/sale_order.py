# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    tasks_ids = fields.Many2many('project.task', compute='_compute_tasks_ids',
                                 string='Tasks associated to this sale')

    @api.multi
    def _compute_tasks_ids(self):
        for line in self:
            line.tasks_ids = self.env['project.task'].search([
                ('sale_line_id', '=', line.id)])
