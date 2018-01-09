# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleSubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'

    automatic_renewal = fields.Selection(
        [('none', 'None'),
         ('same_dur', 'Same Duration'),
         ('month', 'Month'),
         ('quarter', 'Quarter'),
         ('semester', 'Semester')]
    )
    customer_prior_notice = fields.Integer(
        string='Customer Prior Notice',
    )
    advance_invoice_date = fields.Integer(
        help="Set the delta on the invoice date and the invoiced period."
             "If 0, the start of the invoiced period will be the same as"
             " the invoice date."
             "If > 0, it sets the invoiced period with a delta (in months) "
             "from the invoice date",
        default=0
    )
