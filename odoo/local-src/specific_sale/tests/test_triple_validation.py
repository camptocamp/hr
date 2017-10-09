# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import BaseCase


class TestSaleTripleValidation(BaseCase):

    @classmethod
    def setup_records(cls):
        cls.so = cls.env['sale.order'].sudo(cls.sale_user).create({
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'partner_shipping_id': cls.partner.id,
            'order_line': [
                (0, 0, {'name': p.name,
                        'product_id': p.id,
                        'product_uom_qty': 2,
                        'product_uom': p.uom_id.id,
                        'price_unit': p.list_price})
                for (_, p) in cls.products.iteritems()
            ],
            'pricelist_id': cls.env.ref('product.list0').id,
        })

    def test_so_state_options_order(self):
        selection = self.env['sale.order']._fields['state'].selection
        idxs = {state[0]: idx for idx, state in enumerate(selection)}
        self.assertEqual(idxs['draft'], 0)
        self.assertEqual(idxs['to_approve_tech'], 1)
        self.assertEqual(idxs['refused'], 2)

    def test_three_steps_under_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        # as simple user -> need approval (amounts won't match)
        so.sudo(self.sale_user).action_confirm()
        self.assertEquals(so.state, 'to_approve')

    def test_three_steps_technical_manager(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation as tech manager -> approved
        so.sudo(self.technical_manager).action_confirm()
        self.assertEquals(so.state, 'sale')

    def test_three_steps_manager(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation as manager -> need tech approval
        so.sudo(self.sale_manager).action_confirm()
        self.assertEquals(so.state, 'to_approve_tech')
        # approve quotation as tech manager -> approved
        so.sudo(self.technical_manager).action_approve()
        self.assertEquals(so.state, 'sale')

    def test_three_steps_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = so.amount_total
        # confirm quotation
        so.sudo(self.sale_user).action_confirm()
        self.assertEquals(so.state, 'to_approve')
        so.sudo(self.sale_manager).action_confirm()
        self.assertEquals(so.state, 'to_approve_tech')
        so.sudo(self.technical_manager).action_approve()
        self.assertEquals(so.state, 'sale')

    def test_three_steps_above_limit(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        so.sudo(self.sale_user).action_confirm()
        self.assertEquals(so.state, 'to_approve')
        so.sudo(self.sale_manager).action_confirm()
        self.assertEquals(so.state, 'to_approve_tech')
        so.sudo(self.technical_manager).action_approve()
        self.assertEquals(so.state, 'sale')

    def test_three_steps_technical_manager_bypass(self):
        so = self.so
        so.company_id.sudo().so_double_validation = 'bso_three_step'
        so.company_id.sudo().so_double_validation_amount = 10
        # confirm quotation
        so.sudo(self.sale_user).action_confirm()
        self.assertEquals(so.state, 'to_approve')
        # direct confirm by technical manager
        so.sudo(self.technical_manager).action_approve()
        self.assertEquals(so.state, 'sale')
