# -*- coding: utf-8 -*-
from odoo import models, fields


class UbersmithServicePlan(models.Model):
    _name = 'ubersmith.service.plan'
    _rec_name = 'title'

    plan_id = fields.Char(
        string="Plan ID",
    )
    code = fields.Char(
        string="Code",
    )
    title = fields.Char(
        string="Title",
    )
    category = fields.Char(
        string="Category",
    )
    period = fields.Selection([
        ('0', 'One Time'),
        ('1', 'Monthly'),
        ('3', 'Quarterly'),
        ('6', 'Semi'),
        ('12', 'Annual'),
    ])
    bill_type = fields.Selection([
        ('period', 'By period'),
        ('month', 'By month'),
    ])
    post_renew = fields.Boolean(
        string='Bill in arrears',
    )
    bill_prior = fields.Boolean(
        string='Bill in advance',
    )
    quantity = fields.Float(
        string="Default Quantity",
    )
    price = fields.Float(
        string="Price",
    )
    cost = fields.Float(
        string="Cost",
    )
    brand_id = fields.Many2one(
        string="Brand ID",
        comodel_name="ubersmith.brand"
    )
    state = fields.Selection(
        selection=[('1', 'Active plans'),
                   ('0', 'Deactivated plans'),
                   ('2', 'All'),
                   ('3', 'All services'),
                   ('4', 'All active services')],
        string="Service plan State",
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    odoo_product_id = fields.Many2one(
        string="Product ID",
        comodel_name="product.product"
    )

    def create_or_sync_plans(self):
        brands = self.env['ubersmith.brand'].search([])
        for brand in brands:
            brand.create_or_sync_brand_service_plans()

    def create_or_sync_plan(self, plan_dict):
        plan_id = plan_dict['plan_id']
        service_plan = self.search([('plan_id', '=', plan_id)])
        if not service_plan:
            return self.create({
                'plan_id': plan_id,
                'code': plan_dict['code'],
                'title': plan_dict['title'],
                'category': plan_dict['category'],
                'period': plan_dict['period'],
                'bill_type': self._get_bill_type(
                    plan_dict['bill_type']),
                'bill_prior': self.convert_to_bool(
                    plan_dict['bill_prior']),
                'post_renew': self.convert_to_bool(
                    plan_dict['post_renew']),
                'quantity': self.convert_to_float(
                    plan_dict['quantity']),
                'price': self.convert_to_float(
                    plan_dict['price']),
                'cost': self.convert_to_float(
                    plan_dict['cost']),
                'brand_id': self.brand_id.get_brand(plan_dict['class_id']).id,
                'state': plan_dict['active']
            })
        service_plan.sync_service_plan(plan_dict)

    @staticmethod
    def _get_bill_type(bill_type):
        if bill_type == '0':
            return 'period'
        elif bill_type == '1':
            return 'month'
        else:
            return 'other'

    def sync_service_plan(self, service_plan_dict):
        service_plan_values = {}
        if self.code != service_plan_dict.get('code'):
            service_plan_values['code'] = service_plan_dict.get('code')
        if self.title != service_plan_dict.get('title'):
            service_plan_values['title'] = service_plan_dict.get('title')
        if self.category != service_plan_dict.get('category'):
            service_plan_values['category'] = service_plan_dict.get('category')
        if self.period != service_plan_dict.get('period'):
            service_plan_values['period'] = service_plan_dict.get('period')
        bill_type = self._get_bill_type(service_plan_dict.get('bill_type'))
        if self.bill_type != bill_type:
            service_plan_values['bill_type'] = bill_type
        bill_prior = self.convert_to_bool(service_plan_dict['bill_prior'])
        if self.bill_prior != bill_prior:
            service_plan_values['bill_prior'] = bill_prior
        post_renew = self.convert_to_bool(service_plan_dict['post_renew'])
        if self.post_renew != post_renew:
            service_plan_values['post_renew'] = post_renew
        quantity = self.convert_to_float(service_plan_dict['quantity'])
        if self.quantity != quantity:
            service_plan_values['quantity'] = quantity
        price = self.convert_to_float(service_plan_dict['price'])
        if self.price != price:
            service_plan_values['price'] = price
        cost = self.convert_to_float(service_plan_dict['cost'])
        if self.cost != cost:
            service_plan_values['cost'] = cost
        if self.brand_id.brand_id != service_plan_dict['class_id']:
            brand = self.brand_id.get_brand(service_plan_dict['class_id'])
            service_plan_values['brand_id'] = brand.id
        if self.state != service_plan_dict['active']:
            service_plan_values['state'] = service_plan_dict['active']
        self.write(service_plan_values)

    @staticmethod
    def convert_to_bool(str_value):
        return bool(int(str_value))

    @staticmethod
    def convert_to_float(str_value):
        return float(str_value)

    def get_plan_by_code(self, code):
        return self.search([
            ('code', '=', code)
        ], limit=1).id
