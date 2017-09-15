# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class InvoiceTimesheetReport(models.AbstractModel):

    _name = 'report.invoice_timesheet_report.report_invoice_timesheet'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'invoice_timesheet_report.report_invoice_timesheet')
        docs = self.env['account.invoice'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
        }
        return report_obj.render(
            'invoice_timesheet_report.report_invoice_timesheet', docargs)
