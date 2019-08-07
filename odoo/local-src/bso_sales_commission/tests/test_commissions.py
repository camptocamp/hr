# -*- coding: utf-8 -*-

from odoo.addons.bso_sales_commission.tests.common import TestCommon


class TestCommissions(TestCommon):

    def test_create_quarter_annual_after_so_confirmation(self):
        so = self.so
        # before confirmation
        quarter_id = so.salesperson_commission_line_ids.quarter_id
        self.assertFalse(quarter_id.id)
        # confirmation
        so_confirmed = self._create_dealsheet_and_confirm(so)
        # after confirmation
        quarter_id = so_confirmed.salesperson_commission_line_ids.quarter_id

        self.assertTrue(quarter_id.id)
        self.assertTrue(quarter_id.annual_id)

    def test_assign_quarter_annual_if_exist(self):
        so1 = self._create_dealsheet_and_confirm(self.so)
        commission_line1 = so1.salesperson_commission_line_ids

        so2 = self._create_dealsheet_and_confirm(self.so_copy)
        commission_line2 = so2.salesperson_commission_line_ids

        self.assertEqual(commission_line1.quarter_id,
                         commission_line2.quarter_id)
        self.assertEqual(commission_line1.quarter_id.annual_id,
                         commission_line2.quarter_id.annual_id)

    def test_assign_target_if_exists(self):
        original_salesperson_target = self.original_salesperson_target
        so1 = self._create_dealsheet_and_confirm(self.so)
        commission_line = so1.salesperson_commission_line_ids

        self.assertEqual(commission_line.quarter_id.target_id,
                         original_salesperson_target)

    def test_commission_line_formula(self):
        so = self._create_dealsheet_and_confirm(self.so)
        line = so.salesperson_commission_line_ids

        # expected_earnings_nrr = so.dealsheet_id.nrr => 10000
        self.assertEqual(line.earnings_nrr, 10000)

        # expected_earnings_mrr = so.dealsheet_id.mrr  => 5000
        self.assertEqual(line.earnings_mrr, 5000)

        # expected_margin_nrr = so.dealsheet_id.nrm*expected_earnings_nrr/100
        # => 2000
        self.assertEqual(line.margin_nrr, 2000)

        # com_nrm_weight = line.get_parameter('nrm_factor')
        # coef = line.subscription_management_coef
        # expected_com_nrr = com_nrm_weight * coef * expected_margin_nrr
        # => 300
        self.assertEqual(line.commission_nrr, 300)

        # com_mrr_weight = line.get_parameter('mrr_factor')
        # duration_weight = line.get_parameter('duration')
        # expected_com_mrr = \
        #   expected_earnings_mrr * com_mrr_weight * duration_weight * coef
        # => 3500
        self.assertEqual(line.commission_mrr, 2500)

        # expected_com_total = expected_com_mrr + expected_com_nrr
        # => 3500 + 300 = 3800
        self.assertEqual(line.commission, 2800)

    def test_commission_quarter_formula(self):
        so = self._create_dealsheet_and_confirm(self.so)
        quarter = so.salesperson_commission_line_ids.quarter_id

        self.assertEqual(quarter.earnings_nrr, 10000)
        self.assertEqual(quarter.earnings_mrr, 5000)

        # expected_attainment_nrr = quarter.earnings_nrr / quarter.target_nrr
        self.assertEqual(quarter.attainment_ratio_nrr, 0.277777777777778)

        # expected_attainment_mrr = quarter.earnings_mrr / quarter.target_mrr
        self.assertEqual(quarter.attainment_ratio_mrr, 0.185185185185185)

        # attainment_factor_nrr =
        #   quarter.get_payout_value(attainment_ratio_nrr)
        self.assertEqual(quarter.attainment_factor_nrr, 0.5)

        # attainment_factor_mrr =
        #   quarter.get_payout_value(attainment_ratio_mrr)
        self.assertEqual(quarter.attainment_factor_mrr, 0.5)

        self.assertEqual(quarter.commission_nrr, 300)
        self.assertEqual(quarter.commission_mrr, 2500)
        self.assertEqual(quarter.commission, 2800)

        # payout_nrr = quarter.total_commission_nrr*attainment_factor_nrr
        self.assertEqual(quarter.payout_nrr, 150)

        # payout_mrr = quarter.total_commission_mrr*attainment_factor_mrr
        self.assertEqual(quarter.payout_mrr, 1250)

        self.assertEqual(quarter.payout, 1400)
