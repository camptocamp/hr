# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Invoice Timesheet Report",
    "summary": "Print timesheet report from invoice",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.camptocamp.com/",
    "author": "Camptocamp SA,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account",
        "sale_timesheet",
        "project",
    ],
    "data": [
        "report/invoice_timesheet.xml",
        "views/product.xml"
    ],
    "application": False,
    "installable": True,
}
