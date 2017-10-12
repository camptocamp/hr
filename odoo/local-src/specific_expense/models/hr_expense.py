# -*- coding: utf-8 -*-
# © 2016 Camptocamp (alexandre.fayolle@camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.onchange('company_id')
    def onchange_company(self):
        # restricts to the product of the company
        if self.company_id:
            return {
                'domain': {
                    'product_id': ['&',
                                   ('company_id', '=', self.company_id.id),
                                   ('can_be_expensed', '=', 1)],
                }
            }

    @api.constrains('company_id', 'product_id')
    def _check_product_company(self):
        for rec in self:
            if rec.company_id != rec.product_id.company_id:
                raise ValidationError(
                    _('An expense sheets cannot use '
                      'products from another company. '
                      'Product %s in in %s, while the '
                      'expense is in %s') %
                    (rec.product_id.name,
                     rec.product_id.company_id,
                     rec.company_id.name)
                )
