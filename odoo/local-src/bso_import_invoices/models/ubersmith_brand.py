# -*- coding: utf-8 -*-
from odoo import models, fields, api


class UbersmithBrand(models.Model):
    _name = 'ubersmith.brand'
    _rec_name = 'class_name'

    brand_id = fields.Char(
        string="Brand ID",
    )
    class_name = fields.Char(
        string="Class name",
    )
    currency_id = fields.Many2one(
        string="Ubersmith Currency",
        comodel_name='ubersmith.currency'
    )
    class_abbr = fields.Char(
        string="Class abbr",
    )
    serverurl = fields.Char(
        string="Server URL",
    )
    class_name_en_GB = fields.Char(
        string="Class name en GB",
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
    )

    @api.model
    def create(self, values):
        brand_id = values.get('brand_id')
        if brand_id:
            values['company_id'] = self.sudo().get_company(brand_id)
        return super(UbersmithBrand, self).create(values)

    def get_company(self, brand_id):
        # /!\ hard coded for tests purposes
        # if brand_id in ['1', '2', '3', '7']:
        #     return self._get_company_by_name('IX Reach Ltd')
        # if brand_id in ['6', '9', '10', '11']:
        #     return self._get_company_by_name('IX Reach International Ltd')
        if brand_id in ['1', '2', '3', '7', '6', '9', '10', '11']:
            return self._get_company_by_name('BSO Network Solutions Ltd')

    def _get_company_by_name(self, name):
        return self.company_id.search([
            ('name', '=', name)
        ]).id

    def create_or_sync_brands(self):
        api = self.env['ubersmith.api']
        brands = api.get_brands()
        for brand_id, brand_dict in brands.iteritems():
            self.create_or_sync_brand(brand_dict)

    def create_or_sync_brand(self, brand_dict):
        brand = self.get_brand(brand_dict['class_id'])
        if not brand:
            return self.create_brand(brand_dict)
        brand.sync_brand(brand_dict)
        return brand

    def get_brand(self, brand_id):
        return self.search([
            ('brand_id', '=', brand_id)
        ])

    def create_brand(self, brand_dict):
        return self.create({
            'brand_id': brand_dict['class_id'],
            'class_name': brand_dict['class_name'],
            'class_abbr': brand_dict['class_abbr'],
            'serverurl': brand_dict['serverurl'],
            'class_name_en_GB': brand_dict['class_name_en_GB'],
            'currency_id': self.sudo().currency_id.get_or_create_currency(
                brand_dict['currency_id'],
                brand_dict['class_name'])
        })

    def sync_brand(self, brand_dict):
        brand_values = {}
        if self.currency_id.currency_id != brand_dict.get('currency_id') \
                or self.class_name != brand_dict.get('class_name'):
            currency_id = self.currency_id.get_or_create_currency(
                brand_dict['currency_id'],
                brand_dict['class_name'])
            brand_values['currency_id'] = currency_id
        if self.class_name != brand_dict.get('class_name'):
            brand_values['class_name'] = brand_dict.get('class_name')
        if self.class_abbr != brand_dict.get('class_abbr'):
            brand_values['class_abbr'] = brand_dict.get('class_abbr')
        if self.serverurl != brand_dict.get('serverurl'):
            brand_values['serverurl'] = brand_dict.get('serverurl')
        if self.class_name_en_GB != brand_dict.get('class_name_en_GB'):
            brand_values['class_name_en_GB'] = brand_dict.get(
                'class_name_en_GB')
        self.write(brand_values)

    def create_or_sync_brand_service_plans(self):
        api = self.env['ubersmith.api']
        plans_dict = api.get_service_plans(self.brand_id).iteritems()
        plan_model = self.env['ubersmith.service.plan']
        for plan_id, plan_dict in plans_dict:
            plan_model.create_or_sync_plan(plan_dict)

    def create_or_sync_brand_taxes(self):
        api = self.env['ubersmith.api']
        taxes_dict = api.get_tax_list(self.brand_id).iteritems()
        for tax_id, tax_dict in taxes_dict:
            tax = self.env['ubersmith.tax'].search([('tax_id', '=', tax_id)])
            if not tax:
                rate = float(tax_dict['rate'])
                self.env['ubersmith.tax'].create({
                    'tax_id': tax_id,
                    'name': tax_dict['name'],
                    'brand_id': self.id,
                    'rate': rate,
                })
