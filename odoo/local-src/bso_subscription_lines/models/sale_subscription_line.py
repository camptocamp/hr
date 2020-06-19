# -*- coding: utf-8 -*-
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner',
        related='analytic_account_id.partner_id',
        store=True
    )
    price_subtotal = fields.Float(
        store=True
    )
