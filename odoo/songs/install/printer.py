# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def enable_printing_on_invoice_report(ctx):
    report = ctx.env.ref('account.account_invoices')
    action = ctx.env.ref('base_report_to_printer.printing_action_1')
    report.property_printing_action_id = action


@anthem.log
def main(ctx):
    enable_printing_on_invoice_report(ctx)
