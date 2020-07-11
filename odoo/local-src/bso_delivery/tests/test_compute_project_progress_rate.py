from odoo.tests import common
from datetime import datetime


@common.at_install(False)
@common.post_install(True)
class TestComputeProjectProgressRate(common.TransactionCase):
    def setUp(self):
        super(TestComputeProjectProgressRate, self).setUp()

        partner = self.env['res.partner'].create(dict(name="test prtnr"))
        stock_location = self.env.ref('stock.stock_location_stock')
        customer_location = self.env.ref('stock.stock_location_customers')

        # create product.category
        pc = self.env['product.category'].create({
            'name': 'test category',
            'property_cost_method': 'standard',
            # 'property_valuation': 'perpetual'
        })

        # create product.product record
        product_data = {
            'name': 'test product',
            'categ_id': pc.id,
            'type': 'service',
            'invoice_policy': 'order',
            'track_service': 'manual'
        }
        product = self.env['product.product'].create(product_data)

        # create stock.picking records
        sp_1 = self.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
        })

        sp_2 = self.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
        })

        self.sp = [sp_1.id, sp_2.id]
        product.picking_ids = self.sp
        # create stock.pack.operation records
        pack_data = {
            'date': datetime.now(),
            'product_id': product.id,
            'location_id': stock_location.id,
            'location_dest_id': customer_location.id,
            'product_qty': 5,
            'picking_id': sp_1.id
        }
        self.spo_1 = self.env['stock.pack.operation'].create(pack_data)

        pack_data['picking_id'] = sp_2.id

        self.spo_2 = self.env['stock.pack.operation'].create(pack_data)

        # create sale.order record
        so_data = {
            'name': 'test sale order',
            'partner_id': partner.id,
            'product_id': product.id,
            'amount_untaxed': 157
        }
        self.so = self.env['sale.order'].create(so_data)

        # create sale.order.line records
        self.ol_1 = self.env['sale.order.line'].create({
            'name': '',
            'order_id': self.so.id,
            'price_unit': 10,
            'product_id': product.id,
            'product_uom_qty': 5
        })
        self.ol_2 = self.env['sale.order.line'].create({
            'name': '',
            'order_id': self.so.id,
            'price_unit': 30,
            'product_id': product.id,
            'product_uom_qty': 2
        })

        self.delivery = self.env['delivery.project'].create({
            'sale_order_id': self.so.id,
        })

    def test_compute_project_progress_rate_no_stock_picking(self):
        self.assertEqual(len(self.delivery.sale_order_id.picking_ids), 0)
        self.assertEqual(self.delivery.progress_rate, 100)

    def test_compute_project_progress_rate_stock_picking(self):
        sale_order = self.env['sale.order'].browse(self.so.id)
        sale_order.picking_ids = self.sp

        packop = self.env['stock.pack.operation'].browse(self.spo_1.id)
        packop.qty_done = 5

        delivery = self.env['delivery.project'].browse(self.delivery.id)
        self.assertNotEqual(delivery.progress_rate, 100)
