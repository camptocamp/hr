# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_half = fields.Boolean(
        string="Is half"
    )

    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0,
                    product=None, partner=None):
        res = super(AccountTax, self).compute_all(price_unit, currency,
                                                  quantity, product, partner)
        if len(res['taxes']) <= 1:
            return res

        idx = self._get_idx_is_half_and_include_base(res['taxes'])
        if idx < 0:
            return res

        base = res['taxes'][idx]['base']
        for tax_dict in res['taxes'][idx:]:
            tax = self.browse(tax_dict['id'])
            tax_base = base
            tax_amount = tax._compute_amount(tax_base, price_unit,
                                             quantity, product,
                                             partner)
            if tax.include_base_amount and not tax.is_half:
                base += tax_amount
            if tax.include_base_amount and tax.is_half:
                base += 2 * tax_amount
            tax_dict['base'] = tax_base
            tax_dict['amount'] = tax_amount
        return res

    def _get_idx_is_half_and_include_base(self, taxes):
        for idx, tax_dict in enumerate(taxes):
            tax = self.browse(tax_dict['id'])
            if tax.include_base_amount and tax.is_half:
                return idx
        return -1
