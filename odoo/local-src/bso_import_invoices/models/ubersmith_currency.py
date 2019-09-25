# -*- coding: utf-8 -*-
import re

from odoo import models, fields


class UbersmithCurrency(models.Model):
    _name = 'ubersmith.currency'
    _rec_name = 'currency_id'

    currency_id = fields.Char(
        string='Currency ID'
    )
    name = fields.Char(
        string='Name'
    )
    odoo_currency_id = fields.Many2one(
        string='Odoo Currency ID',
        comodel_name='res.currency'
    )

    def get_or_create_currency(self, currency_ref, name):
        match = re.search(r"\((?P<name>[A-Z]+)\)", name)
        name = match.group('name') if match else False
        odoo_currency_id = self.odoo_currency_id.search([
            ('name', '=', name)
        ]).id
        currency_id = self.search(
            [('currency_id', '=', currency_ref)]).id
        if not currency_id:
            currency_id = self.create({
                'currency_id': currency_ref,
                'name': name,
                'odoo_currency_id': odoo_currency_id
            }).id
        return currency_id
