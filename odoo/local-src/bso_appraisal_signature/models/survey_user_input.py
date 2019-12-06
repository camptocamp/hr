from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import AccessError


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    signature = fields.Binary(
        string='Signature'
    )
    connected_partner = fields.Many2one(
        string='Connected Partner',
        comodel_name='res.partner',
        compute='_compute_my_response'
    )
    is_my_response = fields.Boolean(
        string='My Response',
        compute='_compute_my_response'
    )
    appraisal_state = fields.Selection(
        string='Appraisal State',
        related='appraisal_id.state'
    )

    @api.multi
    def write(self, vals):
        for uinput in self:
            appraisal_id = uinput.appraisal_id
            if (
                    appraisal_id.manager_ids and
                    appraisal_id.count_sent_survey ==
                    appraisal_id.count_completed_survey):
                signatures = self.search(
                    [('appraisal_id', '=', uinput.appraisal_id.id)]
                ).mapped('signature')
                if signatures and all(signatures):
                    uinput.appraisal_id.write({'state': 'done'})
        return super(SurveyUserInput, self).write(vals)

    @api.multi
    def button_modify_answers(self):
        self.ensure_one()
        form_view_action = {
            'type': 'ir.actions.act_url',
            'url': '{}/{}'.format(self.survey_id.public_url, self.token),
            'target': 'new',
            'res_id': self.id,
        }
        if self.env.uid == SUPERUSER_ID:
            return form_view_action
        if not self.is_my_response:
            raise AccessError(
                _('You can not modify other users answers'))
        if self.appraisal_id.state == 'done':
            raise AccessError(
                _('You can not modify your answers at this stage'))
        self.sudo().write({'state': 'new'})
        return form_view_action

    @api.multi
    def _compute_my_response(self):
        for uinput in self:
            uinput.connected_partner = self.env.user.partner_id
            uinput.is_my_response = (
                    uinput.partner_id.id == uinput.connected_partner.id)

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
