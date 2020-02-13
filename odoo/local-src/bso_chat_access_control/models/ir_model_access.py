from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    perm_chat = fields.Boolean('Chat Write Access', default=False)

    @api.model
    def create(self, values):
        if values.get('perm_write'):
            values['perm_chat'] = True
        return super(IrModelAccess, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('perm_write'):
            values['perm_chat'] = True
        return super(IrModelAccess, self).write(values)

    @api.multi
    def check_chat_write_access(self):
        if self.env.uid == SUPERUSER_ID:
            return
        access = self.env['ir.model.access'].search([
            ('perm_chat', '=', True),
            ('group_id', 'in', self.env.user.groups_id.ids),
            ('model_id', '=', self.env.cache['target_model'])
        ])
        if not access:
            raise exceptions.AccessError(
                _("Sorry, you are not allowed to modify this document.")
            )
