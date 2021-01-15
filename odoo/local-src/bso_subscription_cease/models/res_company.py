from odoo import models


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'mail.thread']
