from odoo import models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        if not self.env.user.lead_notification_active:
            return super(
                CrmLead, self.with_context(tracking_disable=True)
            ).create(vals)
        return super(CrmLead, self).create(vals)

    @api.model
    def _message_get_auto_subscribe_fields(
            self, updated_fields, auto_follow_fields=None):
        user_field_lst = super(
            CrmLead, self)._message_get_auto_subscribe_fields(
            updated_fields, auto_follow_fields)
        if ('user_id' in user_field_lst and
                not self.user_id.lead_notification_active):
            user_field_lst.remove('user_id')
        return user_field_lst
