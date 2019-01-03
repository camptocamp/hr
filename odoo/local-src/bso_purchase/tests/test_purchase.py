# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from dateutil.relativedelta import relativedelta
import mock

from .common import TestBsoPurchaseCommon, CURRENT_PATH

STOCK_MOD = 'odoo.addons.stock'


class TestPurchase(TestBsoPurchaseCommon):

    def test_create_update_qty(self):
        self.po.button_confirm()
        self.assertEqual(self.po.state, 'purchase')
        picking = self.po.picking_ids[0]
        picking.do_transfer()
        self.assertEqual(10.0, picking.move_lines.product_uom_qty)

    def test_auto_invoicing_group_monthly_end_of_term(self):
        """Auto invoicing grouping PO by vendor + monthly + end of term."""
        group_supplier_invoice = True
        period, mode = 'monthly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-06-30"
        expected_inv_quantity = 0.53 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_monthly_end_of_term_after_end(self):
        """
        Auto invoicing grouping PO by vendor + monthly + end of term
        + continue_after_end = True
        """

        group_supplier_invoice = True
        period, mode = 'monthly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 1 * 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_group_monthly_start_of_term(self):
        """Auto invoicing grouping PO by vendor + monthly + start of term."""
        group_supplier_invoice = True
        period, mode = 'monthly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = (1 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-08-01"
        expected_inv_end_date = "2018-08-31"
        expected_inv_quantity = 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_monthly_start_of_term_after_end(self):
        """
        Auto invoicing grouping PO by vendor + monthly + start of term
        + continue_after_end is True
        """
        group_supplier_invoice = True
        period, mode = 'monthly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 1 * 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_group_quarterly_end_of_term(self):
        """Auto invoicing grouping PO by vendor + quarterly + end of term."""
        group_supplier_invoice = True
        period, mode = 'quarterly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-06-30"
        expected_inv_quantity = 0.53 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-10-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-09-30"
        expected_inv_quantity = 3 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_quarterly_end_of_term_after_end(self):
        """Auto invoicing grouping PO by vendor + quarterly + end of term
        + continue_after_end = True
        """
        group_supplier_invoice = True
        period, mode = 'quarterly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_group_quarterly_start_of_term(self):
        """Auto invoicing grouping PO by vendor + quarterly + start of term."""
        group_supplier_invoice = True
        period, mode = 'quarterly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2018-09-30"
        expected_inv_quantity = (3 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-10-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-10-01"
        expected_inv_end_date = "2018-12-31"
        expected_inv_quantity = 3 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_quarterly_start_of_term_after_end(self):
        """Auto invoicing grouping PO by vendor + quarterly + start of term
        + continue_after_end = True
        """
        group_supplier_invoice = True
        period, mode = 'quarterly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 1 * 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_group_yearly_end_of_term(self):
        """Auto invoicing grouping PO by vendor + yearly + end of term."""
        group_supplier_invoice = True
        period, mode = 'yearly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2019-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-12-31"
        expected_inv_quantity = (6 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2020-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2019-01-01"
        expected_inv_end_date = "2019-12-31"
        expected_inv_quantity = 12 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_yearly_end_of_term_after_end(self):
        """Auto invoicing grouping PO by vendor + yearly + end of term
        + continue_after_end = True"""
        group_supplier_invoice = True
        period, mode = 'yearly', 'end_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 1 * 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_group_yearly_start_of_term(self):
        """Auto invoicing grouping PO by vendor + yearly + start of term."""
        group_supplier_invoice = True
        period, mode = 'yearly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2019-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2019-12-31"
        expected_inv_quantity = (0.53 + 6 + 12) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2020-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2020-01-01"
        expected_inv_end_date = "2020-12-31"
        expected_inv_quantity = 12 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_group_yearly_start_of_term_after_end(self):
        """Auto invoicing grouping PO by vendor + yearly + start of term
        + continue_after_end = True
        """
        group_supplier_invoice = True
        period, mode = 'yearly', 'start_of_term'
        expected_nb_invoices = 1
        # First time we invoice the PO line
        fake_today_po = "2018-07-01"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 1 * 10
        continue_after_end = True
        subscr_duration = 0

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration,
            continue_after_end)

    def test_auto_invoicing_no_group_monthly_end_of_term(self):
        """Auto invoicing without grouping PO by vendor
        + monthly + end of term.
        """
        group_supplier_invoice = False
        period, mode = 'monthly', 'end_of_term'
        expected_nb_invoices = 2    # 2 PO to invoice
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-06-30"
        expected_inv_quantity = 0.53 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_no_group_monthly_start_of_term(self):
        """Auto invoicing without grouping PO by vendor
        + monthly + start of term.
        """
        group_supplier_invoice = False
        period, mode = 'monthly', 'start_of_term'
        expected_nb_invoices = 2    # 2 PO to invoice
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2018-07-31"
        expected_inv_quantity = (1 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-08-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-08-01"
        expected_inv_end_date = "2018-08-31"
        expected_inv_quantity = 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_no_group_quarterly_end_of_term(self):
        """Auto invoicing without grouping PO by vendor
        + quarterly + end of term.
        """
        group_supplier_invoice = False
        period, mode = 'quarterly', 'end_of_term'
        expected_nb_invoices = 2    # 2 PO to invoice
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-06-30"
        expected_inv_quantity = 0.53 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-10-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-07-01"
        expected_inv_end_date = "2018-09-30"
        expected_inv_quantity = 3 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_no_group_quarterly_start_of_term(self):
        """Auto invoicing without grouping PO by vendor
        + quarterly + start of term.
        """
        group_supplier_invoice = False
        period, mode = 'quarterly', 'start_of_term'
        expected_nb_invoices = 2    # 2 PO to invoice
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2018-07-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2018-09-30"
        expected_inv_quantity = (3 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2018-10-01"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2018-10-01"
        expected_inv_end_date = "2018-12-31"
        expected_inv_quantity = 3 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_no_group_yearly_end_of_term(self):
        """Auto invoicing grouping PO by vendor + yearly + end of term."""
        group_supplier_invoice = False
        period, mode = 'yearly', 'end_of_term'
        expected_nb_invoices = 2
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2019-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po
        expected_inv_end_date = "2018-12-31"
        expected_inv_quantity = (6 + 0.53) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2020-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2019-01-01"
        expected_inv_end_date = "2019-12-31"
        expected_inv_quantity = 12 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def test_auto_invoicing_no_group_yearly_start_of_term(self):
        """Auto invoicing grouping PO by vendor + yearly + start of term."""
        group_supplier_invoice = False
        period, mode = 'yearly', 'start_of_term'
        expected_nb_invoices = 2
        # First time we invoice the PO line
        fake_today_po = "2018-06-15"
        fake_today_cron = "2019-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = fake_today_po     # Delivery date
        expected_inv_end_date = "2019-12-31"
        expected_inv_quantity = (0.53 + 6 + 12) * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

        # Second time we invoice the PO line
        fake_today_cron = "2020-01-02"
        expected_inv_bill_date = fake_today_cron
        expected_inv_start_date = "2020-01-01"
        expected_inv_end_date = "2020-12-31"
        expected_inv_quantity = 12 * 10

        self.run_test_auto_invoicing(
            period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity)

    def run_test_auto_invoicing(
            self, period, mode, group_supplier_invoice,
            expected_nb_invoices, fake_today_po, fake_today_cron,
            expected_inv_bill_date,
            expected_inv_start_date, expected_inv_end_date,
            expected_inv_quantity,
            subscr_duration=36,
            continue_after_end=False):
        self.partner_id.write({
            'group_supplier_invoice': group_supplier_invoice,
            'automatic_supplier_invoicing': True,
            'supplier_invoicing_period': period,
            'supplier_invoicing_mode': mode,
        })
        # Prepare the POs to be invoiced
        self.po.onchange_partner_id()
        self.po2.onchange_partner_id()
        with mock.patch(CURRENT_PATH + '.fields.Date.today') as fnct_today:
            fnct_today.return_value = fake_today_po
            today_date = fields.Date.from_string(fields.Date.today())
        end = today_date + relativedelta(months=subscr_duration)
        self.po.subscr_date_start = self.po2.subscr_date_start = fake_today_po
        # To be sure that the 'yearly' related tests can be run, we create
        # a subscription of 3 years (36 months) as we generate two invoices
        # from the same subscription, separated by one month/quarter/year
        # depending of the test.
        # A 1 year subscription is OK to tests this process with a monthly or
        # quarterly period, but for yearly it's not enough.
        self.po.subscr_duration = self.po2.subscr_duration = subscr_duration
        self.po.subscr_date_end = self.po2.subscr_date_end = end
        self.po.continue_after_end = continue_after_end
        self.po2.continue_after_end = continue_after_end
        if self.po.state == self.po2.state != 'purchase':
            self.po.button_confirm()
            self.po2.button_confirm()
        with mock.patch(
                STOCK_MOD + '.models.stock_move.time.strftime') as fnct:
            fnct.return_value = fake_today_po
            picking = self.po.picking_ids[0]
            picking2 = self.po2.picking_ids[0]
            if picking.state == picking2.state != 'done':
                picking.do_transfer()
                picking2.do_transfer()

        if continue_after_end:
            period = 'monthly'
        # Check number of invoices
        invoice_ids = self.AccountInvoice.cron_po_auto_invoice(
            period, mode, fake_today_cron)
        invoices = self.env['account.invoice'].browse(invoice_ids)
        invoices.action_invoice_open()
        for invoice in invoices:
            self.assertEqual(invoice.date_invoice, expected_inv_bill_date)
        self.assertEqual(expected_nb_invoices, len(invoices))
        for line in invoices.mapped('invoice_line_ids'):
            # Check the start/end dates
            self.assertEqual(line.start_date, expected_inv_start_date)
            self.assertEqual(line.end_date, expected_inv_end_date)
            # Check the invoiced quantity
            self.assertAlmostEqual(
                line.quantity, expected_inv_quantity, 1)
