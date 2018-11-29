# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from __future__ import division

from odoo import models, api

from dateutil import relativedelta
from calendar import monthrange


class UtilsDuration(models.AbstractModel):
    _name = 'utils.duration'

    @api.model
    def get_month_delta_for_mrc(self, ref_date, delivery_date):
        """ Return the timedelta in month between ref_date and delivery_date"""
        months = 0
        start_date = delivery_date
        while start_date <= ref_date:
            # Calculating each month in the given period separately
            if (ref_date.month == start_date.month and
               ref_date.year == start_date.year):
                end_date = ref_date
            else:
                end_date = start_date + relativedelta.relativedelta(
                    months=+1, day=1)
            delta = relativedelta.relativedelta(end_date, start_date)
            months += delta.months
            if delta.days > 0:
                months += delta.days / monthrange(
                    start_date.year, start_date.month)[1]
            if (end_date == ref_date):
                break
            start_date = end_date
        return months
