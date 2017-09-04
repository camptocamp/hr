# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
from datetime import datetime
from calendar import monthrange
from dateutil import relativedelta
from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom.recurring')
    def _compute_qty_delivered_calculated(self):
        """ Used in the view, and to update the qty_delivered regularly """
        for record in self:
            if record.product_uom.recurring:
                qty = record._get_delivered_qty()
                record.qty_delivered_calculated = qty
                record.write({'qty_delivered': qty})
            else:
                record.qty_delivered_calculated = record.qty_delivered

    qty_delivered_calculated = fields.Float(
        string='Delivered',
        compute='_compute_qty_delivered_calculated')

    @api.multi
    def is_delivered_and_invoiced(self):
        self.ensure_one()
        return (bool(self.order_id.subscription_id) and
                self.product_uom_qty <= self.qty_delivered and
                self.qty_invoiced == self.qty_delivered)

    @api.multi
    @api.depends('order_id.subscription_id', 'product_uom', 'qty_delivered',
                 'product_uom_qty', 'qty_invoiced')
    def _compute_invoice_status(self):
        super(SaleOrderLine, self)._compute_invoice_status()
        for line in self:
            if line.product_uom.recurring:
                has_subscription_contract = bool(line.order_id.subscription_id)
                if line.qty_delivered > 0 and not has_subscription_contract:
                    line.invoice_status = 'to invoice'
                elif line.is_delivered_and_invoiced():
                    line.invoice_status = 'invoiced'

    @api.multi
    def _get_delivered_qty(self):
        """ Change the delivered_qty calculation method for MRC product"""
        self.ensure_one()
        qty = 0
        ref_date = self.env.context.get('ref_date_mrc_delivery')
        if ref_date:
            ref_date = fields.Datetime.from_string(ref_date)
        else:
            ref_date = datetime.now()
        if self.product_uom.recurring:
            stock_moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('scrapped', '=', False),
                ('procurement_id', 'in', self.procurement_ids.ids),
            ])
            for move in stock_moves:
                delivery_date = fields.Datetime.from_string(move.date)
                month_ratio = self.get_month_delta_for_mrc(
                        ref_date, delivery_date)
                qty += move.product_uom_qty * month_ratio
        else:
            qty = super(SaleOrderLine, self)._get_delivered_qty()
        return qty

    def mrc_fully_delivered(self):
        """ For MRC product verify with stock.move if the order line
            is completely delivered
        """
        self.ensure_one()
        if not self.product_uom.recurring:
            return True
        qty = 0.0
        for move in self.procurement_ids.mapped('move_ids').filtered(
                lambda r: r.state == 'done' and not r.scrapped):
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id:
                    qty += move.product_uom._compute_quantity(
                            move.product_uom_qty, self.product_uom)
            elif (move.location_dest_id.usage == "internal"
                  and move.to_refund_so):
                qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, self.product_uom)
        return qty == self.product_uom_qty

    @staticmethod
    def get_month_delta_for_mrc(ref_date, delivery_date):
        """ Return the timedelta in month between ref_date and delivery_date"""
        months = 0
        start_date = delivery_date
        while True:
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
