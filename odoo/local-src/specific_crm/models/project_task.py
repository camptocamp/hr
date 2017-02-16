# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    lead_id = fields.Many2one(comodel_name='crm.lead',
                              string="Linked Opportunity")
    survey_input_lines = fields.One2many(related='lead_id.survey_input_lines')
