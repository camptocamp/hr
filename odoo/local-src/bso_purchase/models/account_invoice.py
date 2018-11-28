# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from dateutil.relativedelta import relativedelta
import datetime
from calendar import monthrange


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def get_current_quarter(self, date_str):
        """Returns the current quarter number of `date_str`.

            >>> self.get_current_quarter("2018-02-15")  # First quarter
            1
            >>> self.get_current_quarter("2018-06-22")  # Second
            2
            >>> self.get_current_quarter("2018-07-04")  # Third
            3
            >>> self.get_current_quarter("2018-11-23")  # Fourth
            4

        :param date_str: date as string
        :return: quarter number as integer
        """
        date_ = fields.Date.from_string(date_str)
        return (date_.month - 1) // 3 + 1

    @api.model
    def get_quarter_dates(self, date_str):
        """Get start/end dates of the quarter matching give date.

            >>> self.get_quarter_dates("2018-02-15")    # First quarter
            ('2018-01-01', '2018-03-31')
            >>> self.get_quarter_dates("2018-06-22")    # Second
            ('2018-04-01', '2018-06-30')
            >>> self.get_quarter_dates("2018-07-04")    # Third
            ('2018-07-01', '2018-09-30')
            >>> self.get_quarter_dates("2018-11-23")    # Fourth
            ('2018-10-01', '2018-12-31')

        :param date_str: date as string
        :return: tuple (start_date, end_date)
        """
        quarter = self.get_current_quarter(date_str)
        year = fields.Date.from_string(date_str).year
        first_month = 3 * quarter - 2
        last_month = 3 * quarter
        first_day = datetime.date(year, first_month, 1)
        last_day = datetime.date(
            year, last_month, monthrange(year, last_month)[1])
        return (
            fields.Date.to_string(first_day),
            fields.Date.to_string(last_day))

    @api.model
    def get_po_auto_invoice_ref_date(
            self, invoicing_period, invoicing_mode, today):
        """Get reference date used to fetch the PO to invoice.

        Look up for purchase.order based on the current date, the
        `invoicing_period` (monthly / quarterly) and the `invoicing_mode`
        (end of term / start of term).

        Assuming we are the 2018-11-22:

            >>> self.get_po_auto_invoice_ref_date('monthly', 'end_of_term')
            '2018-11-22'
            >>> self.get_po_auto_invoice_ref_date('monthly', 'start_of_term')
            '2018-12-01'
            >>> self.get_po_auto_invoice_ref_date('quarterly', 'end_of_term')
            '2018-11-22'
            >>> self.get_po_auto_invoice_ref_date('quarterly', 'start_of_term')
            '2019-01-01'

        :param invoicing_period: 'monthly' or 'quarterly'
        :param invoicing_mode: 'start_of_term' or 'end_of_term'
        :param today: the date of 'today', or another date to fake the system
            on dev/integration environments (for test purpose only).
        :return: date as string
        """
        # Default: if end_of_term, ref_date = today
        ref_date = today
        if invoicing_mode == 'start_of_term':
            # monthly:      ref_date = first day of next month
            if invoicing_period == 'monthly':
                ref_date_dt = fields.Date.from_string(ref_date)
                next_month_first_day = (
                    ref_date_dt + relativedelta(months=1, day=1))
                ref_date = fields.Date.to_string(next_month_first_day)
            # quarterly:    ref_date = first day of next quarter
            elif invoicing_period == 'quarterly':
                quarter_end_date = self.get_quarter_dates(ref_date)[1]
                quarter_end_date_dt = fields.Date.from_string(quarter_end_date)
                next_quarter_first_day = (
                    quarter_end_date_dt + relativedelta(days=1))
                ref_date = fields.Date.to_string(next_quarter_first_day)
        return ref_date

    @api.model
    def cron_po_auto_invoice(
            self, invoicing_period, invoicing_mode, today=None):
        """Generate supplier invoices from purchase orders.

        Invoices are generated following several criteria:
            - monthly, end of term (ref. date = today)
            - monthly, start of term (ref. date = first day of the month)
            - quarterly, end of term (ref. date = today)
            - quarterly, start of term (ref. date = first day of quarter)
        The reference date is computed based on the selected combination.
        Purchase orders can also be grouped in one invoice if the supplier
        is configured as such.

        :param invoicing_period: 'monthly' or 'quarterly'
        :param invoicing_mode: 'end_of_term' or 'start_of_term'
        :param today: the date of 'today' to use to fake the system
            on dev/integration environments (for test purpose only)
        :return: a list of generated invoice IDs
        """
        today = today or fields.Date.today()
        ref_date = self.get_po_auto_invoice_ref_date(
            invoicing_period, invoicing_mode, today)
        # = Collect the purchase orders to invoice =
        vendors = self.env['res.partner'].browse()
        invoices = self.env['account.invoice'].browse()
        purchases = self.env['purchase.order'].search(
            [('state', '=', 'purchase'),
             ('supplier_invoicing_period', '=', invoicing_period),
             ('supplier_invoicing_mode', '=', invoicing_mode),
             ('subscr_date_end', '>', ref_date)])
        data_dict = {}
        purchases = self._check_po_in_invoice(purchases)
        for purchase in purchases:
            company = purchase.company_id
            if purchase.partner_id.automatic_supplier_invoicing:
                vendors |= purchase.partner_id
            if company not in data_dict:
                data_dict[company] = {
                    purchase.partner_id: {purchase.currency_id: [purchase]}}
            else:
                if purchase.partner_id not in data_dict[company]:
                    data_dict[company][purchase.partner_id] = {
                        purchase.currency_id: [purchase]}
                else:
                    dcp = data_dict[company][purchase.partner_id]
                    if purchase.currency_id not in dcp:
                        dcp[purchase.currency_id] = [purchase]
                    else:
                        dcp[purchase.currency_id].append(purchase)

        # = Invoice the purchase orders =
        for vendor in vendors:
            if vendor.group_supplier_invoice:
                # Group all PO in one invoice
                for comp, vendor_dict in data_dict.iteritems():
                    if vendor in vendor_dict:
                        for curr, po_list in vendor_dict[vendor].iteritems():
                            inv = self.with_context(
                                force_company=comp.id,
                                default_company_id=comp.id,
                                journal_type='purchase',
                                po_auto_invoice_ref_date=ref_date,
                                type='in_invoice').create(
                                    {'partner_id': vendor.id,
                                     'type': 'in_invoice',
                                     'date_invoice': today,
                                     'currency_id': curr.id})
                            inv._onchange_partner_id()
                            for po in po_list:
                                inv.write({'purchase_id': po.id})
                                # Force the onchange trigger
                                inv.purchase_order_change()
                            invoices |= inv
            else:
                # Create one INV per PO
                for po in purchases.filtered(lambda r: r.partner_id == vendor):
                    inv = self.with_context(
                        force_company=po.company_id.id,
                        default_company_id=po.company_id.id,
                        journal_type='purchase',
                        po_auto_invoice_ref_date=ref_date,
                        type='in_invoice').create(
                            {'partner_id': vendor.id,
                             'type': 'in_invoice',
                             'date_invoice': today,
                             'currency_id': po.currency_id.id,
                             'purchase_id': po.id})
                    inv._onchange_partner_id()
                    # Force the onchange trigger
                    inv.purchase_order_change()
                    invoices |= inv
            # Force computation of taxes
            invoices.compute_taxes()

        # Reset the quantity received on all PO lines
        purchases.mapped('order_line')._compute_qty_received()
        return invoices.ids

    @api.model
    def _check_po_in_invoice(self, purchases):
        ''' The goal is to filter purchases which are already going to be
            invoiced.
        '''
        InvLine = self.env['account.invoice.line']
        for po in purchases:
            inv_lines = InvLine.search([('purchase_id', '=', po.id),
                                        ('invoice_id.state', '=', 'draft')])
            for line in inv_lines:
                purchases -= line.purchase_id
        return purchases

    @api.model
    def get_line_dates(
            self, invoicing_period, invoicing_mode, ref_date, po_line):
        """Get invoice line start and end dates.

        The dates depend on the invoice state of the PO line
        (already invoiced or not), the invoicing period/mode and
        the reference date.
        """
        dates = {'start_date': False, 'end_date': False}
        if invoicing_mode == 'end_of_term':
            # NOTE: ref_date == today, assuming it is right after the month
            # (or quarter) to invoice (probably the 1st of the month)
            if invoicing_period == 'monthly':
                today = fields.Date.from_string(ref_date)
                start_date_dt = today - relativedelta(months=1, day=1)
                end_date_dt = (
                    start_date_dt +
                    relativedelta(months=1, day=1) -
                    relativedelta(days=1))
                dates['start_date'] = fields.Date.to_string(start_date_dt)
                dates['end_date'] = fields.Date.to_string(end_date_dt)
            elif invoicing_period == 'quarterly':
                today = fields.Date.from_string(ref_date)
                previous_month_dt = today - relativedelta(months=1)
                previous_month = fields.Date.to_string(previous_month_dt)
                quarter_dates = self.get_quarter_dates(previous_month)
                dates['start_date'] = quarter_dates[0]
                dates['end_date'] = quarter_dates[1]
        elif invoicing_mode == 'start_of_term':
            # NOTE: ref_date == first day of the next month
            # so the start/end dates are the ones from the previous month
            if invoicing_period == 'monthly':
                first_day = (
                    fields.Date.from_string(ref_date) -
                    relativedelta(months=1, day=1))
                last_day = (
                    first_day +
                    relativedelta(months=1, day=1) -
                    relativedelta(days=1))
                dates['start_date'] = fields.Date.to_string(first_day)
                dates['end_date'] = fields.Date.to_string(last_day)
            # NOTE: ref_date == first day of the next quarter
            # so the start/end dates are the ones from the previous quarter
            elif invoicing_period == 'quarterly':
                current_quarter_dt = (
                    fields.Date.from_string(ref_date) -
                    relativedelta(months=1))
                current_quarter = fields.Date.to_string(current_quarter_dt)
                quarter_dates = self.get_quarter_dates(current_quarter)
                dates['start_date'] = quarter_dates[0]
                dates['end_date'] = quarter_dates[1]
        # Special case: if the PO line is invoiced for the first time , the
        # start date is the earliest delivery date
        if invoicing_period and invoicing_mode:
            already_invoiced = self.env['account.invoice.line'].search(
                [('purchase_line_id', '=', po_line.id)])
            if not already_invoiced:
                moves = self.env['stock.move'].search([
                    ('purchase_line_id', '=', po_line.id),
                    ('state', '=', 'done')])
                if moves:
                    sorted_moves = moves.sorted('date')
                    delivery_date = sorted_moves[0].date
                    dates['start_date'] = delivery_date
        return dates

    def _prepare_invoice_line_from_po_line(self, line):
        """Overloaded to set some data on the invoice line:

            - the `start_date` and `end_date` fields
            - the right quantity to invoice based on the end date

        If the PO `line` is invoiced for the first time, its `start_date` is
        set to the delivery date.
        """
        ref_date = self.env.context.get('po_auto_invoice_ref_date')
        dates = {}
        if line.product_id.recurring_invoice and ref_date:
            dates = self.get_line_dates(
                line.order_id.supplier_invoicing_period,
                line.order_id.supplier_invoicing_mode,
                ref_date, line)
            # Compute the right quantity received (to invoice)
            # before calling 'super()'
            # FIXME ref_date or end_date?
            line._compute_qty_received(dates['end_date'])
        res = super(
            AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        # Update start+end dates
        res.update(dates)
        return res
