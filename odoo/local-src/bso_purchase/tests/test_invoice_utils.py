# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import mock

from odoo.tests import common
from odoo import fields

from .common import CURRENT_PATH


class TestInvoiceUtils(common.SavepointCase):

    def test_update_dates(self):
        with mock.patch(CURRENT_PATH + '.fields.Date.today') as fnct_today:
            fnct_today.return_value = "2018-06-15"
            today = fields.Date.today()
            # monthly
            data = self.env['account.invoice.line'].update_dates(today, 1)
            self.assertEqual(data['start_date'], '2018-06-01')
            self.assertEqual(data['end_date'], '2018-06-30')
            # quarterly
            data = self.env['account.invoice.line'].update_dates(today, 3)
            self.assertEqual(data['start_date'], '2018-06-01')
            self.assertEqual(data['end_date'], '2018-08-31')

    def test_get_current_quarter(self):
        invoice_model = self.env['account.invoice']
        self.assertEqual(invoice_model.get_current_quarter("2018-02-15"), 1)
        self.assertEqual(invoice_model.get_current_quarter("2018-06-22"), 2)
        self.assertEqual(invoice_model.get_current_quarter("2018-07-04"), 3)
        self.assertEqual(invoice_model.get_current_quarter("2018-11-23"), 4)

    def test_get_quarter_dates(self):
        invoice_model = self.env['account.invoice']
        self.assertEqual(
            invoice_model.get_quarter_dates("2018-02-15"),
            ('2018-01-01', '2018-03-31'))
        self.assertEqual(
            invoice_model.get_quarter_dates("2018-06-22"),
            ('2018-04-01', '2018-06-30'))
        self.assertEqual(
            invoice_model.get_quarter_dates("2018-07-04"),
            ('2018-07-01', '2018-09-30'))
        self.assertEqual(
            invoice_model.get_quarter_dates("2018-11-23"),
            ('2018-10-01', '2018-12-31'))

    def test_auto_invoice_ref_date_monthly_end_of_term(self):
        period, mode = 'monthly', 'end_of_term'
        fake_today = "2018-06-15"
        expected = "2018-06-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected, ref_date)
        fake_today = "2018-07-02"
        expected = "2018-07-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected, ref_date)

    def test_auto_invoice_ref_date_quarterly_end_of_term(self):
        period, mode = 'quarterly', 'end_of_term'
        fake_today = "2018-06-15"
        expected = "2018-04-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected, ref_date)
        fake_today = "2018-07-02"
        expected = "2018-07-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected, ref_date)

    def test_auto_invoice_ref_date_monthly_start_of_term(self):
        period, mode = 'monthly', 'start_of_term'
        fake_today = "2018-06-15"
        expected_ref_date = "2018-07-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected_ref_date, ref_date)
        fake_today = "2018-07-02"
        expected_ref_date = "2018-08-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected_ref_date, ref_date)

    def test_auto_invoice_ref_date_quarterly_start_of_term(self):
        period, mode = 'quarterly', 'start_of_term'
        fake_today = "2018-06-15"
        expected_ref_date = "2018-07-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected_ref_date, ref_date)
        fake_today = "2018-07-02"
        expected_ref_date = "2018-10-01"
        ref_date = self.env[
            'account.invoice'].get_po_auto_invoice_ref_date(
                period, mode, fake_today)
        self.assertEqual(expected_ref_date, ref_date)
