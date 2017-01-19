# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    survey_id = fields.Many2one(comodel_name='survey.survey',
                                string="Default survey for this team")
    project_id = fields.Many2one(comodel_name='project.project',
                                 string="Default project for this team")
