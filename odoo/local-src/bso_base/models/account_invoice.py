# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from dateutil.relativedelta import relativedelta


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def update_dates(self, today, interval=1):
        today_dt = fields.Date.from_string(today)
        first_day = today_dt.replace(day=1)
        last_day = (today_dt +
                    relativedelta(months=interval, day=1) -
                    relativedelta(days=1)
                    )
        return {'start_date': fields.Date.to_string(first_day),
                'end_date': fields.Date.to_string(last_day)
                }
