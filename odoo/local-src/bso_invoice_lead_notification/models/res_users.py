from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    lead_notification_active = fields.Boolean(
        string='Leads notifications',
        default=True
    )
