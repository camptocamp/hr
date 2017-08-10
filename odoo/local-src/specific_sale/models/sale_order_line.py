# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from dateutil import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def write(self, values):
        res = super(SaleOrderLine, self).write(values)
        for record in self:
            if record.order_id.all_mrc_delivered():
                record.order_id.create_contract()
        return res

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
                elif self.is_delivered_and_invoiced():
                    line.invoice_status = 'invoiced'

    @api.multi
    def _get_delivered_qty(self):
        """ Change the delivered_qty calculation method for MRC product"""
        self.ensure_one()
        qty = 0
        ref_date = (self.env.context.get('ref_date_mrc_delivery')
                    or fields.datetime.now())
        if self.product_uom.recurring:
            stock_moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
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

    @staticmethod
    def get_month_delta_for_mrc(ref_date, delivery_date):
        """ Return the timedelta in month between ref_date and delivery_date"""
        days_since_delivery = relativedelta.relativedelta(
                ref_date, delivery_date).days
        days_since_start_month_delivery = (days_since_delivery +
                                           delivery_date.day - 1)
        if days_since_start_month_delivery > 0:
            return days_since_delivery / days_since_start_month_delivery
        return 0
