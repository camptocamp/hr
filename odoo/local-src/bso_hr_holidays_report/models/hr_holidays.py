from datetime import datetime, date, time

from dateutil.relativedelta import *
from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class HrHolidays(models.Model):
    _inherit = "hr.holidays"
    is_reported = fields.Boolean(string='Is reported')

    @api.constrains('state')
    def _check_leave_state(self):
        today = datetime.combine(date.today(), time())
        for holiday in self:
            if holiday.date_from and holiday.date_from < str(today):
                raise ValidationError(_('You can not update a passed leave'))

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
            ('date_from', '<=', str(date_delta)),
            ('date_from', '>', str(today)),
        ])
