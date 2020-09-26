from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    _mail_post_access = 'read'
