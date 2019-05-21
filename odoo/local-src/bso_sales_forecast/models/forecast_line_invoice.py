# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ForecastLineInvoice(models.Model):
    _name = 'forecast.line.invoice'
    _description = 'Forecast Line Invoice'
    # _inherit = "mail.thread"

    line_id = fields.Many2one(
        string='Line',
        comodel_name='forecast.line',
        delegate=True,
        ondelete='cascade',
        required=True,
    )
    invoice_line_id = fields.Many2one(
        string='Invoice Line',
        comodel_name='account.invoice.line',
        readonly=True
    )
    invoice_id = fields.Many2one(
        string='Account invoice',
        comodel_name='account.invoice',
        related='invoice_line_id.invoice_id',
        readonly=True
    )
    product_id = fields.Many2one(
        string='Product',
        related='invoice_line_id.product_id',
        readonly=True
    )
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='product.category',
        related='product_id.categ_id',
        readonly=True,
    )
    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner',
        related='invoice_line_id.partner_id',
        readonly=True,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        related='invoice_id.date_invoice',
        readonly=True,
    )
    form_id = fields.Many2one(
        string='Open',
        comodel_name='forecast.line.invoice',
        readonly=True,
    )

    @api.model
    def create(self, values):
        invoice_line = self.invoice_line_id.browse(
            values['invoice_line_id'])
        invoice = invoice_line.invoice_id
        report = self.line_id.report_id.browse(values['report_id'])

        date_invoice = invoice.date_invoice
        amount = invoice_line.price_subtotal
        values['currency_id'] = invoice.currency_id.id
        values['type'] = self.get_type(invoice, invoice_line)
        month_amounts = self.line_id.get_month_amounts(date_invoice,
                                                       date_invoice, report,
                                                       amount)
        values.update(month_amounts)
        rec = super(ForecastLineInvoice, self).create(values)
        rec.form_id = rec.id
        return rec

    @api.model
    def get_type(self, invoice, invoice_line):
        invoice_type = self.get_invoice_type(invoice)
        categ_id = invoice_line.product_id.categ_id
        if not invoice_type:
            return 'unknown_i'
        if invoice.partner_id.bso_companies:
            return 'intercompany_one_off_%s' % invoice_type
        elif self._is_child_of(categ_id, 'goods'):
            return 'hardware_%s' % invoice_type
        else:
            return 'services_%s' % invoice_type

    @staticmethod
    def get_invoice_type(invoice):
        invoice_types = {
            'out_invoice': 'r_i',  # Revenue invoice
            'out_refund': 'r_i',
            'in_invoice': 'c_i',  # Cost invoice
            'in_refund': 'c_i',
        }
        return invoice_types.get(invoice.type)

    @staticmethod
    def _is_child_of(categ_id, parent):
        if categ_id.name == parent:
            return True
        if categ_id.parent_id.name == parent:
            return True
