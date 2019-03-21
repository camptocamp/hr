from odoo import models, fields, api, exceptions

from datetime import datetime
from collections import namedtuple


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    start_date = fields.Date()
    end_date = fields.Date()
