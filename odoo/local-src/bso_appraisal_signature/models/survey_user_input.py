from odoo import models, fields, api


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    signature = fields.Binary(
        string='Signature'
    )
    connected_user = fields.Many2one(
        string='Connected User',
        comodel_name='res.users',
        compute='_compute_my_response'
    )
    is_my_response = fields.Boolean(
        string='My Response',
        compute='_compute_my_response'
    )

    @api.multi
    def _compute_my_response(self):
        for uinput in self:
            uinput.connected_user = self.env.user
            uinput.is_my_response = (
                    uinput.partner_id.user_id == uinput.connected_user)

    @api.multi
    def action_sign(self):
        self.ensure_one()
        return {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': self.env.ref(
                'bso_appraisal_signature.survey_user_input_form').id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'
