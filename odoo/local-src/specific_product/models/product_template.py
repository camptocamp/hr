# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_default_uomid(self):
        if self.recurring_invoice:
            return self.env.ref('__setup__.product_unit_month',
                                raise_if_not_found=False)

    uom_id = fields.Many2one(
            default=lambda self: self._compute_default_uomid()
    )

    @api.onchange('recurring_invoice')
    def set_invoicing_policy(self):
        if self.recurring_invoice:
            self.invoice_policy = 'delivery'
        else:
            self.invoice_policy = 'order'

    @api.constrains('uom_id', 'recurring_invoice')
    def _check_categ_id(self):
        if not (self.recurring_invoice == self.uom_id.recurring):
            raise ValidationError(_('The unit of measure is not compatible '
                                    'with the subscription type'))
