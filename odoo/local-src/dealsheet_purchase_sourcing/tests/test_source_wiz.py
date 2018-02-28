# -*- coding: utf-8 -*-
# Author: Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import BaseTestCase


class WizTestCase(BaseTestCase):

    def _init_wiz(self):
        wiz = self.wiz_model.sudo(self.sale_manager.id).with_context(
            default_dealsheet_id=self.dealsheet.id).create({})
        wiz.onchange_dealsheet_id()
        return wiz

    def test_load_wizard_init(self):
        wiz = self._init_wiz()
        # lines to source and sourcing lines must be the same as the order's
        self.assertEqual(len(self.dealsheet.cost_upfront_line),
                         len(wiz.sourcing_line_ids))
        self.assertEqual(len(self.dealsheet.cost_upfront_line),
                         len(wiz.to_source_line_ids))
        # and no sourced line yet
        self.assertEqual(0, len(wiz.sourced_line_ids))

    def test_supplier_domain(self):
        wiz = self._init_wiz()
        suppliers = wiz._get_available_suppliers()
        for supp in self.all_suppliers:
            self.assertIn(supp, suppliers)
        # then we set a supplier on a source line
        pid = self.prod_gcard.id
        line = wiz.line_ids.filtered(
            lambda x: x.product_id.id == pid)
        prod_suppliers = self.prod_suppliers[pid]
        line.supplier_id = prod_suppliers[0].id
        suppliers = wiz._get_available_suppliers()
        # we should get all suppliers but the one already assigned
        expected = self.all_suppliers.filtered(
            lambda x: x.id != line.supplier_id.id)
        for supp in expected:
            self.assertIn(supp, suppliers)
        self.assertNotIn(line.supplier_id, suppliers)

    def test_change_supplier(self):
        wiz = self._init_wiz()
        wiz.supplier_id = self.prod_suppliers[self.prod_gcard.id][0]
        wiz.onchange_supplier_id()
        # source lines are reloaded, all of them as there was no supplier set
        self.assertEqual(len(wiz.sourcing_line_ids), 4)
        for line in wiz.sourcing_line_ids:
            # supplier is set on sourcing line
            self.assertEqual(line.supplier_id, wiz.supplier_id)
            # but not on source line
            self.assertFalse(line.source_line_id.supplier_id)

    def test_action_source_all(self):
        wiz = self._init_wiz()
        wiz.supplier_id = self.prod_suppliers[self.prod_gcard.id][0]
        wiz.onchange_supplier_id()
        wiz.action_source()
        for line in wiz.line_ids:
            # supplier is set on wiz line
            self.assertEqual(line.supplier_id, wiz.supplier_id)
        # sourced lines: all
        self.assertEqual(len(wiz.sourced_line_ids), 4)
        # lines to source: none
        self.assertEqual(len(wiz.to_source_line_ids), 0)

    def _source_partial(self, wiz, supplier, pid_to_exclude=None):
        wiz.supplier_id = supplier
        wiz.onchange_supplier_id()
        if pid_to_exclude:
            # delete a sourcing line
            wiz.sourcing_line_ids.filtered(
                lambda x: x.product_id.id == pid_to_exclude).unlink()
        wiz.action_source()

    def test_action_source_partial(self):
        supplier = self.prod_suppliers[self.prod_gcard.id][0]
        wiz = self._init_wiz()
        self._source_partial(wiz, supplier, pid_to_exclude=self.prod_iMac.id)
        # sourced lines: all but the one with excluded product
        self.assertEqual(len(wiz.sourced_line_ids), 3)
        # lines to source: the excluded one
        self.assertEqual(len(wiz.to_source_line_ids), 1)
        self.assertEqual(wiz.to_source_line_ids[0].product_id, self.prod_iMac)

    def test_create_orders(self):
        supplier1 = self.prod_suppliers[self.prod_gcard.id][0]
        supplier2 = self.prod_suppliers[self.prod_appleWLKB.id][0]
        wiz = self._init_wiz()
        # source 3 items w/ supplier1
        self._source_partial(wiz, supplier1, pid_to_exclude=self.prod_iMac.id)
        # the rest w/ supplier2
        self._source_partial(wiz, supplier2)
        ids = wiz._create_orders()
        self.assertEqual(len(ids), 2)
        order1 = self.env['purchase.order'].browse(ids[0])
        order2 = self.env['purchase.order'].browse(ids[1])
        self.assertEqual(len(order1.order_line), 3)
        self.assertEqual(len(order2.order_line), 1)
        # verify that SO lines are linked to PO lines
        po_lines = order1.order_line + order2.order_line
        for prod in self.prods:
            pid = prod.id
            wiz_line = wiz.line_ids.filtered(lambda x: x.product_id.id == pid)
            po_line = po_lines.filtered(lambda x: x.product_id.id == pid)
            self.assertEqual(wiz_line.so_line_id.sourcing_purchase_line_id.id,
                             po_line.id)
            self.assertEqual(wiz_line.so_line_id.id,
                             po_line.sourced_sale_line_id.id)
