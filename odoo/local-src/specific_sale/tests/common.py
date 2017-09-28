# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SingleTransactionCase


class BaseCase(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(BaseCase, cls).setUpClass()
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.products = {
            'prod_order': cls.env.ref('product.product_order_01'),
            'prod_del': cls.env.ref('product.product_delivery_01'),
            'serv_order': cls.env.ref('product.service_order_01'),
            'serv_del': cls.env.ref('product.service_delivery'),
        }
        cls.company = cls.env.ref('base.main_company')
        cls.company.currency_id = cls.env.ref('base.USD')
        cls.setup_users()
        cls.setup_records()

    @classmethod
    def setup_records(cls):
        pass

    @classmethod
    def setup_users(cls):
        group_sale_manager = cls.env.ref('sales_team.group_sale_manager')
        group_user = cls.env.ref('sales_team.group_sale_salesman')
        group_proj_manager = cls.env.ref('project.group_project_manager')
        cls.user_model = cls.env['res.users'].with_context({
            'no_reset_password': True,
            'tracking_disable': True,
        })
        # website_contract/models/sale_subscription._recurring_create_invoice
        # does commit (!) so we end up w/ real records in DB
        # and if you run tests more than once you gonna get an error
        # when users are already there...
        cls.sale_manager = \
            cls.user_model.search([('login', '=', 'sale_manager')])
        if not cls.sale_manager:
            cls.sale_manager = cls.user_model.create({
                'name': 'Sale Manager',
                'login': 'sale_manager',
                'email': 'sale_managerm@example.com',
                'notify_email': 'always',
                'groups_id': [(6, 0, [group_sale_manager.id])]
            })
        cls.sale_user = \
            cls.user_model.search([('login', '=', 'sale_user')])
        if not cls.sale_user:
            cls.sale_user = cls.user_model.create({
                'name': 'Sale User',
                'login': 'sale_user',
                'email': 'saleuser@example.com',
                'notify_email': 'always',
                'groups_id': [(6, 0, [group_user.id, group_proj_manager.id])]
            })
        group_technical_manager = cls.env.ref(
            'specific_security.group_technical_mgmt')
        cls.technical_manager = \
            cls.user_model.search([('login', '=', 'technical_manager')])
        if not cls.technical_manager:
            cls.technical_manager = cls.user_model.create({
                'name': 'Technical Manager Petit Pierre',
                'login': 'technical_manager',
                'alias_name': 'tipierre',
                'email': 'p.p@example.com',
                'notify_email': 'always',
                'groups_id': [(6, 0, [group_technical_manager.id,
                                      group_proj_manager.id])]
            })
