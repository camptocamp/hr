# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    lead_id = fields.Many2one(related='user_input_id.lead_id',
                              store=True)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    lead_id = fields.Many2one(comodel_name="crm.lead")
