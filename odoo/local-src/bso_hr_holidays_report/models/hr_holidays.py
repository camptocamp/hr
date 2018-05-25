from datetime import datetime, date, time

from dateutil.relativedelta import relativedelta
from odoo import api, models


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def auto_validate_leaves(self):
        leaves = self._get_non_validated_leaves()
        for line in leaves:
            line.state = "validate"

    def _get_non_validated_leaves(self):
        today = datetime.combine(date.today(), time())
        date_delta = today + relativedelta(days=2)
        return self.env['hr.holidays'].search([
            ('state', 'in', ['confirm']),
            ('date_from', '>', str(today)),
            ('date_from', '<', str(date_delta)),
        ])
