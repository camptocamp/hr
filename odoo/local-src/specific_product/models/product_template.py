# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_default_uomid(self):
        if self.recurring_invoice:
            return self.ref('__setup__.product_unit_month')

    uom_id = fields.Many2one(
        default=_compute_default_uomid
    )

    @api.onchange('recurring_invoice')
    def setInvoicingPolicy(self):
        if self.recurring_invoice:
            self.invoice_policy = 'delivery'
        else:
            self.invoice_policy = 'order'

    @api.constrains('uom_id', 'recurring_invoice')
    def _check_categ_id(self):
        if not (self.recurring_invoice == self.uom_id.recurring):
            raise ValidationError('The unit of measure is not compatible with'
                                  'the subscription type')
