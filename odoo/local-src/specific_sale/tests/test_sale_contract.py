# -*- coding: utf-8 -*-
from odoo.addons.sale_contract.tests import common_sale_contract
import odoo.tests.common as common
from odoo import exceptions


class TestContract(common.TransactionCase):

    def setUp(self):
        super(TestContract, self).setUp()
        Contract = self.env['sale.subscription']
        SubTemplate = self.env['sale.subscription.template']
        Product = self.env['product.product']
        ProductTmpl = self.env['product.template']
        TestUsersEnv = self.env['res.users'].with_context(
            {'no_reset_password': True})
        SaleOrder = self.env['sale.order']
        group_portal_id = self.ref('base.group_portal')

        # Test User
        self.user_portal = TestUsersEnv.create({
            'name': 'Rincewind',
            'login': 'rincewind',
            'email': 'rincewind@example.com',
            'groups_id': [(6, 0, [group_portal_id])]
        })
        # Test products
        self.product_tmpl = ProductTmpl.create({
            'name': 'TestProduct',
            'type': 'service',
            'recurring_invoice': True,
            'uom_id': self.ref('product.product_uom_unit'),
            'price': 50.0,
            'standard_price': 50.0,
            'list_price': 50,
        })
        self.product = Product.create({
            'product_tmpl_id': self.product_tmpl.id,
        })
        self.prd2.recurring_invoice = True
        self.prd2 = self.env.ref('product.service_order_01')
        # Test Contract
        self.contract_tmpl = SubTemplate.create({
            'name': 'TestContractTemplate',
            'subscription_template_line_ids': [(
                0, 0,
                {'product_id': self.prd2.id,
                 'name': 'TestRecurringLine',
                 'uom_id': self.product_tmpl.uom_id.id,
                 'actual_quantity': 2,
                 'price': 10,
                 })],
            'recurring_interval': 3,
            # 'recurring_total': 10,
        })
        self.contract = Contract.create({
            'name': 'TestContract',
            'state': 'open',
            'partner_id': self.user_portal.partner_id.id,
            'pricelist_id': self.ref('product.list0'),
            'template_id': self.contract_tmpl.id,
        })
        self.contract.on_change_template()
        self.sale_order = SaleOrder.create({
            'name': 'TestSO',
            'project_id': self.contract.analytic_account_id.id,
            'partner_id': self.user_portal.partner_id.id,
            'partner_invoice_id': self.user_portal.partner_id.id,
            'partner_shipping_id': self.user_portal.partner_id.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})],
            'pricelist_id': self.ref('product.list0'),
        })

    def test_create_invoice(self):
        """ Test SO search overrides """
        # self.contract.recurring_invoice()
        # invoice = self.contract._prepare_invoice_data()
        # lines = self.contract._prepare_invoice_line(line)

        contract_tmpl = self.contract_tmpl
        # contract_tmpl.subscription_template_line_ids[0].write({'price': 10})
        # contract_tmpl.write({'recurring_interval': 3})

        contract = self.contract
        # contract.set_open()
        # contract.write({'template_id': contract_tmpl.id})

        # Doesn't create invoice.line => invoice amount == 0
        invoice = contract._recurring_create_invoice()[0]
        toto = contract.action_subscription_invoice()
        import pdb;pdb.set_trace()
        # self.contract._prepare_invoice_line()
