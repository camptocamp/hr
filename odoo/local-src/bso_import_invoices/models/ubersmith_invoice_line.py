# -*- coding: utf-8 -*-
import re

from odoo import models, fields


class UbersmithInvoiceLine(models.Model):
    _name = 'ubersmith.invoice.line'
    _rec_name = 'line_id'

    line_id = fields.Char(
        string="Invoice Line ID",
    )
    plan_id = fields.Many2one(
        string="Service Plan",
        comodel_name="ubersmith.service.plan"
    )
    description = fields.Char(
        string="Description"
    )
    quantity = fields.Float(
        string="Quantity"
    )
    unit_price = fields.Float(
        string="Unit Price"
    )
    cost = fields.Float(
        string="Cost"
    )
    value = fields.Float(
        string="Value"
    )
    discount = fields.Char(
        string="Discount"
    )
    date_start = fields.Date(
        string="Date start"
    )
    date_end = fields.Date(
        string="Date end"
    )
    period = fields.Integer(
        string="Period"
    )
    tax_ids = fields.Many2many(
        string="Tax",
        comodel_name="ubersmith.tax"
    )
    service_id = fields.Many2one(
        string="Service ID",
        comodel_name='ubersmith.service'
    )
    bill_type = fields.Selection(
        string="Bill Type",
        related="service_id.bill_type"
    )
    invoice_id = fields.Many2one(
        comodel_name="ubersmith.invoice",
        string="Ubersmith Invoice",
        ondelete='cascade',
    )
    odoo_invoice_line_id = fields.Many2one(
        string="Odoo Invoice Line",
        comodel_name="account.invoice.line"
    )
    is_correctly_imported = fields.Boolean(
        string='Correctly imported',
    )

    def get_discount_percentage(self):
        if not self.discount:
            return False
        discount_type = self.service_id.discount_type
        discount_value = float(re.sub(r"[^0-9.]", '', self.discount))
        if discount_type == 'value' and self.unit_price != 0:
            p = self.period or 1
            d = self.unit_price * p * self.quantity
            return discount_value * 100 / d
        elif discount_type == 'percentage':
            return discount_value
        return False
