# -*- coding: utf-8 -*-
from odoo import models, fields, api


class UbersmithTax(models.Model):
    _name = 'ubersmith.tax'
    _rec_name = 'name'

    name = fields.Char(
        string="Name"
    )
    tax_id = fields.Char(
        string="Tax ID"
    )
    brand_id = fields.Many2one(
        string="Brand",
        comodel_name="ubersmith.brand"
    )
    rate = fields.Float(
        string="Rate"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    odoo_tax_id = fields.Many2one(
        string="Tax",
        comodel_name="account.tax"
    )

    @api.model
    def create(self, values):
        brand_id = values.get('brand_id')
        if brand_id and 'rate' in values:
            brand = self.env['ubersmith.brand'].browse(brand_id)
            values['odoo_tax_id'] = self.sudo().get_odoo_tax_id(
                brand.company_id.id,
                values['rate'])
        return super(UbersmithTax, self).create(values)

    def create_or_sync_taxes(self):
        for brand in self.brand_id.search([]):
            brand.create_or_sync_brand_taxes()

    def get_odoo_tax_id(self, company_id, rate):
        return self.odoo_tax_id.search([
            ('company_id', '=', company_id),
            ('type_tax_use', '=', 'sale'),
            ('amount_type', '=', 'percent'),
            ('amount', '=', rate * 100)
        ], limit=1).id

    def get_ubersmith_taxes(self, tax_ids):
        return self.search([
            ('tax_id', 'in', tax_ids)
        ]).ids
