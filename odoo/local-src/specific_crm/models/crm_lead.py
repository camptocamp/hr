# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import uuid
from datetime import datetime, timedelta

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    domain = fields.Text()
    start_date = fields.Date()
    end_date = fields.Date()
    signature_ids = fields.Many2many(comodel_name='res.partner',
                                     string="Signatures")
    project_id = fields.Many2one(comodel_name='project.project')
    survey_id = fields.Many2one(comodel_name='survey.survey')
    survey_input_lines = fields.One2many(
        comodel_name='survey.user_input_line', inverse_name='lead_id',
        string='Surveys answers')
    survey_inputs = fields.One2many(
        comodel_name='survey.user_input', inverse_name='lead_id',
        string='Surveys')
    survey_input_count = fields.Integer(
        string='Survey number', compute='_count_survey_input',
        store=True)
    business_type = fields.Selection(selection=[('injection', 'Injection'),
                                                ('composite', 'Composite')])

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            self.survey_id = self.team_id.survey_id.id
            self.project_id = self.team_id.project_id.id

    @api.depends('survey_inputs')
    def _count_survey_input(self):
        for rec in self:
            rec.survey_input_count = len(rec.survey_inputs)

    @api.multi
    def answer_selected_survey(self):
        self.ensure_one()
        survey_response_obj = self.env['survey.user_input']
        selected_survey = self.survey_id
        # if there's already a survey started (state=skip), relaunch this one
        if self.survey_inputs:
            for sur in self.survey_inputs:
                if sur.survey_id == selected_survey and sur.state != 'done':
                    url = '%s/%s' % (selected_survey.public_url, sur.token)
                    return {
                        'type': 'ir.actions.act_url',
                        'name': "Resume Survey",
                        'target': 'self',
                        'url': url,
                    }
        else:
            # else create a new one

            # generate invitation link for this partner
            # (do not send email to customer)
            token = uuid.uuid4().__str__()
            # create response with token
            now = datetime.now()
            survey_response_obj.create({
                'survey_id': selected_survey.id,
                'deadline': fields.Datetime.to_string(now + timedelta(days=1)),
                'date_create': fields.Datetime.to_string(now),
                'type': 'link',
                'state': 'new',
                'token': token,
                'lead_id': self.id,
                # 'email': self.email
                }
                )
            # get link to the survey
            url = '%s/%s' % (selected_survey.public_url, token)

            # open survey
            return {
                'type': 'ir.actions.act_url',
                'name': "Start Survey",
                'target': 'self',
                # 'target': 'new',
                'url': url,
                }
