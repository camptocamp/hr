# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestComputeAll(TransactionCase):

    def test_case1(self):
        taxes_args_list = [
            {
                'amount': 10,
                'include_base_amount': True,
                'is_half': False,
            },
            {

                'amount': 5,
                'include_base_amount': False,
                'is_half': False
            }
        ]
        invoice = self.create_invoice(taxes_args_list)
        tax2 = invoice.tax_line_ids[1]
        self.assertEquals(tax2.base, 1100)
        self.assertEquals(tax2.amount, 55)

    def test_case2(self):
        taxes_args_list = [
            {
                'amount': 10,
                'include_base_amount': True,
                'is_half': True,
            },
            {

                'amount': 5,
                'include_base_amount': False,
                'is_half': False
            }
        ]
        invoice = self.create_invoice(taxes_args_list)
        tax2 = invoice.tax_line_ids[1]
        self.assertEquals(tax2.base, 1200)
        self.assertEquals(tax2.amount, 60)

    def test_case3(self):
        taxes_args_list = [
            {
                'amount': 10,
                'include_base_amount': False,
                'is_half': False,
            },
            {

                'amount': 5,
                'include_base_amount': True,
                'is_half': True
            },
            {

                'amount': 20,
                'include_base_amount': True,
                'is_half': False
            },
            {

                'amount': 30,
                'include_base_amount': False,
                'is_half': False
            }
        ]
        invoice = self.create_invoice(taxes_args_list)

        tax2 = invoice.tax_line_ids[1]
        self.assertEquals(tax2.base, 1000)
        self.assertEquals(tax2.amount, 50)

        tax3 = invoice.tax_line_ids[2]
        self.assertEquals(tax3.base, 1100)
        self.assertEquals(tax3.amount, 220)

        tax4 = invoice.tax_line_ids[3]
        self.assertEquals(tax4.base, 1320)
        self.assertEquals(tax4.amount, 396)

    def test_case4(self):
        taxes_args_list = [
            {
                'amount': 10,
                'include_base_amount': True,
                'is_half': True,
            },
            {
                'amount': 5,
                'include_base_amount': True,
                'is_half': True
            },
            {
                'amount': 20,
                'include_base_amount': True,
                'is_half': True
            },
            {
                'amount': 30,
                'include_base_amount': False,
                'is_half': False
            }
        ]
        invoice = self.create_invoice(taxes_args_list)

        tax2 = invoice.tax_line_ids[1]
        self.assertEquals(tax2.base, 1200)
        self.assertEquals(tax2.amount, 60)

        tax3 = invoice.tax_line_ids[2]
        self.assertEquals(tax3.base, 1320)
        self.assertEquals(tax3.amount, 264)

        tax4 = invoice.tax_line_ids[3]
        self.assertEquals(tax4.base, 1848)
        self.assertEquals(tax4.amount, 554.4)

    def create_invoice(self, taxes_args_list):
        partner_id = self.env['res.partner'].create({
            'name': 'Test partner',
            'customer': True
        }).id
        currency_id = self.env['res.currency'].search([
            ('name', '=', 'EUR')
        ]).id
        company_id = self.env['res.company'].search([
            ('name', '=', 'BSO Network Solutions SAS')
        ]).id
        journal_id = self.env['account.journal'].create(
            {'name': 'Ventes', 'code': 'V123', 'type': 'sale',
             'company_id': company_id, }).id
        product_id = self.env['product.product'].search([
            ('name', '=', 'MRC Cabinet')]
        ).id
        line_account_id = self.env['account.account'].search([
            ('code', '=', 420201)
        ], limit=1).id
        account_id = self.env['account.account'].search([
            ('code', '=', 411100)
        ], limit=1).id

        tax_ids = self._get_tax_ids(taxes_args_list)

        return self.env['account.invoice'].create({
            'partner_id': partner_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
            'company_id': company_id,
            'account_id': account_id,
            'invoice_line_ids': [(0, 0, {
                'name': 'invoice line',
                'product_id': product_id,
                'account_id': line_account_id,
                'price_unit': 1000,
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
            })]
        })

    def _get_tax_ids(self, taxes_args_list):
        tax_ids = []
        taxes_count = len(taxes_args_list)
        for idx in range(taxes_count):
            tax_dict = taxes_args_list[idx]
            tax = self.env['account.tax'].create({
                'name': 'Tax{}'.format(idx + 1),
                'amount': tax_dict['amount'],
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'include_base_amount': tax_dict['include_base_amount'],
                'is_half': tax_dict['is_half'],
                'sequence': idx + 1,
            })
            tax_ids.append(tax.id)
        return tax_ids
