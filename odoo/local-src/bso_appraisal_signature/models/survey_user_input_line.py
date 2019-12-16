from odoo import models, fields, api


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    raw_answer = fields.Text(
        string='Answer',
        compute='compute_raw_answer',
        store=True
    )

    @api.depends('value_text', 'value_number', 'value_date',
                 'value_free_text', 'value_suggested', 'value_suggested_row')
    def compute_raw_answer(self):
        for uil in self:
            if uil.answer_type == 'suggestion':
                uil.raw_answer = uil['value_suggested'].value
            else:
                uil.raw_answer = uil[
                    'value_%s' % uil.answer_type
                    ] if uil.answer_type else False
