# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import math

from openerp import models, api, fields
from openerp import tools


class HrHolidaysImposed(models.Model):
    _inherit = 'hr.holidays.imposed'

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        """
        If there are no date set for date_to, automatically set one
        8 hours later than the date_from.
        Also update the number_of_days.
        """
        super(HrHolidaysImposed, self).onchange_dates()
        days = self._compute_number_of_days(self.date_to, self.date_from)
        self.number_of_days = days

    def _compute_number_of_days(self, date_to, date_from):
        diff_days = 0
        DATETIME_FORMAT = tools.DEFAULT_SERVER_DATETIME_FORMAT
        if date_from and date_to:
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)

            from_dt_h = fields.Datetime.context_timestamp(self, from_dt)
            from_dt_h1330 = fields.Datetime.context_timestamp(
                self, from_dt).replace(hour=13, minute=30)

            to_dt_h = fields.Datetime.context_timestamp(self, to_dt)
            to_dt_h1330 = fields.Datetime.context_timestamp(
                self, to_dt).replace(hour=13, minute=30)
            if from_dt_h > from_dt_h1330:
                diff_days -= .5
            if to_dt_h < to_dt_h1330:
                diff_days += .5

            date_from2 = fields.Datetime.from_string(date_from)
            date_to2 = fields.Datetime.from_string(date_to)

            date_from2 = date_from2.replace(hour=8, minute=0, second=0)
            date_to2 = date_to2.replace(hour=7, minute=59, second=59)

            if not date_from or not date_to:
                return 0
            days = self._get_number_of_days(date_from, date_to)

            if days or date_to == date_from:
                days = round(math.floor(days))+1

            return days + diff_days
        return 0

    @api.onchange('status_id', 'company_id')
    def onchange_status_id(self):
        if self.status_id.company_id:
            self.company_id = self.status_id.company_id
