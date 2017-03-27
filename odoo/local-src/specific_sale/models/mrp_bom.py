# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    project_task_id = fields.Many2one(
        'project.task',
        string='Project Task',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='project_task_id.project_id',
        readonly=True,
    )
