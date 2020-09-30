from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def action_org_chart(self):
        return {}