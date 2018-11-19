# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class TestPickingUpdateDeliveryDate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPickingUpdateDeliveryDate, cls).setUpClass()
        cls.product_model = cls.env['product.product']
        cls.picking_model = cls.env['stock.picking']
        cls.move_model = cls.env['stock.move']
        # Get some basic data
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        # Create test data
        cls.product = cls.product_model.create(
            {'name': 'Test Product', 'type': 'product'})
        cls.supplier = cls.env['res.partner'].create({
            'name': u"Test Supplier",
            'supplier': True,
        })
        cls.picking_out = cls.picking_model.create({
            'partner_id': cls.supplier.id,
            'picking_type_id': cls.picking_type_out.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
        })
        cls.move_model.create({
            'name': cls.product.name,
            'product_id': cls.product.id,
            'product_uom_qty': 10,
            'product_uom': cls.product.uom_id.id,
            'picking_id': cls.picking_out.id,
            'location_id': cls.stock_location.id,
            'location_dest_id': cls.customer_location.id,
        })
        # Put qty in stock
        cls.change_product_qty(cls.product, 10)
        # Validate the picking
        cls.picking_out.action_confirm()
        cls.picking_out.action_assign()
        cls.picking_out.action_done()
        # Create the wizard
        wiz_update_model = cls.env['wizard.picking.update.delivery_date']
        wiz_update_vals = wiz_update_model.with_context(
            active_model=cls.picking_out._name,
            active_id=cls.picking_out.id).default_get(['picking_id'])
        cls.wiz_update = wiz_update_model.create(wiz_update_vals)

    @classmethod
    def change_product_qty(cls, product, new_qty):
        wiz_model = cls.env['stock.change.product.qty']
        vals = wiz_model.with_context(
            active_model=product._name, active_id=product.id).default_get([])
        vals['new_qty'] = new_qty
        wiz = wiz_model.create(vals)
        wiz.change_product_qty()

    def test_update_delivery_date(self):
        new_delivery_date = '2018-11-18 00:00:00'
        self.wiz_update.delivery_date = new_delivery_date
        self.wiz_update.validate()
        date_done = self.picking_out.date_done
        delivery_date = new_delivery_date
        self.assertEqual(date_done, delivery_date)
        for move in self.picking_out.move_lines:
            move_date = move.date
            self.assertEqual(move.state, 'done')
            self.assertEqual(move_date, delivery_date)
