# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, models, fields


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.multi
    def auto_validate_leaves(self):
        leaves = self._get_non_validated_leaves()
        for line in leaves:
            line.update({
                'state': 'validate'
            })

    @api.model
    def _get_non_validated_leaves(self):
        today = date.today()
        date_delta = today + relativedelta(days=2)
        return self.search([
            ('state', 'in', ['confirm']),
            ('type', 'in', ['remove']),
            ('date_from', '>', fields.Date.to_string(today)),
            ('date_from', '<', fields.Date.to_string(date_delta)),
        ])
