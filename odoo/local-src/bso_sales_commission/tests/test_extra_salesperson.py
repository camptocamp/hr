# -*- coding: utf-8 -*-
from odoo.addons.bso_sales_commission.tests.common import TestCommon


class TestExtraSalesperson(TestCommon):

    def test_so_without_adding_extra_salesperson(self):
        original_salesperson = self.so.user_id
        self._assert_salespeople(original_salesperson)
        self._assert_total_percentages_is_100()

    def test_so_add_extra_salesperson1_to_salespeople(self):
        so = self.so
        original_salesperson = so.user_id
        extra_salesperson1 = self.extra_salesperson1

        # update percentage of original commission line: 50%
        original_commission = so.get_salesperson_commission(
            original_salesperson.id)
        original_commission.write({'percentage': 50})

        # add new commission line: 50%
        so.write({'salesperson_commission_line_ids': [
            (0, 0, {'user_id': extra_salesperson1.id,
                    'percentage': 50})]})

        expected_salespeople = original_salesperson + extra_salesperson1
        self._assert_salespeople(expected_salespeople=expected_salespeople)
        self._assert_total_percentages_is_100()

    def test_so_add_salesperson1_to_salespeople_set_user_id_to_salesperson1(
            self):
        so = self.so
        original_salesperson = so.user_id
        extra_salesperson1 = self.extra_salesperson1

        original_commission = so.get_salesperson_commission(
            original_salesperson.id)
        so.write({
            'salesperson_commission_line_ids': [
                # update percentage of original commission line: 50%
                (1, original_commission.id, {'percentage': 50}),
                # add
                (0, 0, {'user_id': extra_salesperson1.id, 'percentage': 50}),
            ],
        })
        so.write({'user_id': extra_salesperson1.id})
        self._assert_salespeople(expected_salespeople=extra_salesperson1)
        self._assert_total_percentages_is_100()

    def test_so_add_salesperson1_to_salespeople_set_user_id_to_salesperson2(
            self):
        so = self.so
        original_salesperson = so.user_id
        extra_salesperson1 = self.extra_salesperson1
        extra_salesperson2 = self.extra_salesperson2

        original_commission = so.get_salesperson_commission(
            original_salesperson.id)
        so.write({
            'salesperson_commission_line_ids': [
                # update percentage of original commission line: 30%
                (1, original_commission.id, {'percentage': 30}),
                # add
                (0, 0, {'user_id': extra_salesperson1.id, 'percentage': 70}),
            ],
        })
        so.write({'user_id': extra_salesperson2.id})
        expected_salespeople = extra_salesperson1 + extra_salesperson2
        self._assert_salespeople(expected_salespeople=expected_salespeople)
        self._assert_total_percentages_is_100()
