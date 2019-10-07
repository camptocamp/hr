from odoo import models, api, SUPERUSER_ID


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        if vals.get('message_type') != 'notification':
            self.env.cache['target_model'] = vals.get('model')
            self.env['ir.model.access'].check_chat_write_access()
            current_uid = self.env.uid
            try:
                self.env.uid = SUPERUSER_ID
                return super(MailMessage, self).create(vals)
            finally:
                self.env.uid = current_uid
        return super(MailMessage, self).create(vals)
