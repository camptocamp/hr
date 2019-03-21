from odoo import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    start_date = fields.Date()
    end_date = fields.Date()
