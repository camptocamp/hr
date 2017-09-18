# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    hour_block = fields.Boolean(string='Hour block', default=False,
                                help="This checkbox is used on products which "
                                     "are sold as prepaid hour packages and "
                                     "allows to print the invoice timesheet "
                                     "report on invoices using these products")

    @api.multi
    @api.constrains('hour_block', 'type', 'invoice_policy', 'track_service',
                    'uom_id')
    def _check_time_block(self):
        for product in self:
            if product.hour_block:
                if (
                    product.type != 'service' or
                    product.invoice_policy != 'order' or
                    product.track_service != 'task'
                ):
                    raise ValidationError(_(
                        'Hour block product has to be a service, invoiced on '
                        'ordered quantities and use Create a task and track '
                        'hours as Track service.'))
                multi_uom = self.search_count([
                    ('uom_id', '!=', self.env.ref(
                        'product.product_uom_unit').id)])
                if (
                        multi_uom
                        and (product.uom_id != self.env.ref(
                            'product.product_uom_hour')
                             or product.uom_id.category_id != self.env.ref(
                                'product.uom_categ_wtime'))
                ):
                    raise ValidationError(_('Hour block product has to use '
                                            'hour as unit of measure or a '
                                            'unit of measure from Working '
                                            'Time category.'))
