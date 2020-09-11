from odoo import models, api, SUPERUSER_ID, _
from odoo.exceptions import AccessError


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        model = vals.get('model')
        if not model or self.env.user.id == SUPERUSER_ID:
            return super(MailMessage, self).create(vals)
        chat_access = self._has_chat_access(model)
        if not chat_access:
            raise AccessError(
                _("Sorry, you are not allowed to comment on this document."))
        if not chat_access.perm_write:
            try:
                chat_access.sudo().write({'perm_write': True})
                rec = super(MailMessage, self).create(vals)
            finally:
                chat_access.sudo().write({
                    'perm_write': False
                })
            return rec
        return super(MailMessage, self).create(vals)

    def _has_chat_access(self, model_id):
        groups_id = self.env['res.groups'].search(
            [('users', 'in', self.env.uid)]).ids
        return self.env['ir.model.access'].search([
            ('model_id', '=', model_id),
            ('perm_chat', '=', True),
            ('group_id', 'in', groups_id),
        ], limit=1)
