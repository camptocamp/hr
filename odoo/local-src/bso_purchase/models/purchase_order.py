# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from datetime import datetime


class Purchase(models.Model):
    _inherit = 'purchase.order'

    subscr_date_start = fields.Date(
        string='Subscription start',
        states={'cancel': [('readonly', True)]},
    )
    subscr_date_end = fields.Date(string='Subscription end')
    subscr_duration = fields.Integer(
        string='Subscription duration (months)',
        states={'cancel': [('readonly', True)]},
        default=12,
    )
    has_subscription = fields.Boolean(
        string='Has subscription',
        compute='_compute_has_subscription',
        readonly=True
    )

    @api.depends('order_line.product_id')
    def _compute_has_subscription(self):
        line_model = self.env['purchase.order.line']
        domain = [('product_id.recurring_invoice', '=', True)]
        for item in self:
            item.has_subscription = bool(line_model.search(
                domain[:] + [('order_id', '=', item.id)]))


class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_qty_received(self, reference_date=False):
        UtilsDuration = self.env['utils.duration']
        for line in self:
            qty = 0
            # Coming from wizard or var in signature ?
            ref_date = self.env.context.get('ref_date_mrc_delivery')
            if ref_date:
                ref_date = fields.Datetime.from_string(ref_date)
            else:
                ref_date = datetime.now()
            if not line.product_uom.recurring:
                super(PurchaseLine, line)._compute_qty_received()
                continue
            moves = self.env['stock.move'].search([
                ('purchase_line_id', 'in', self.ids),
                ('state', '=', 'done')])
            subscr_date_end = fields.Datetime.from_string(
                line.order_id.subscr_date_end)
            calc_date = (min(ref_date, subscr_date_end)
                         if subscr_date_end else ref_date)
            for move in moves:
                month_ratio = UtilsDuration.get_month_delta_for_mrc(
                    calc_date, fields.Datetime.from_string(move.date))
                qty += move.product_uom_qty * month_ratio
            line.qty_received = qty
