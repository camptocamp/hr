from odoo import models, api, SUPERUSER_ID, _
from odoo.exceptions import AccessError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        model = vals.get('model')
        if not model:
            return super(MailMessage, self).create(vals)
        chat_access = self._has_chat_access(model)
        if not chat_access:
            raise AccessError(
                _("Sorry, you are not allowed to comment on this document."))
        cur_uid = self.env.uid
        try:
            self.env.uid = SUPERUSER_ID
            return super(MailMessage, self).create(vals)
        finally:
            self.env.uid = cur_uid

    def _has_chat_access(self, model_id):
        if self._uid == 1:
            # User root have all accesses
            return True
        return bool(self.env['ir.model.access'].search([
            ('model_id', '=', model_id),
            ('perm_chat', '=', True),
            ('group_id', 'in', self.env.user.groups_id.ids),
        ], limit=1))
