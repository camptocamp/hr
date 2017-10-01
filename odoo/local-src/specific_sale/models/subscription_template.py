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
