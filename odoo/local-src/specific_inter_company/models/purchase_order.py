# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    def _prepare_sale_order_data(self, name, partner, company,
                                 direct_delivery_address):
        values = super(PurchaseOrder, self)._prepare_sale_order_data(
            name, partner, company, direct_delivery_address
        )[0]
        analytic = self.mapped('order_line.account_analytic_id')
        if len(analytic) != 1:
            raise UserError(_('All the lines of the purchase must '
                              'be on the same analytic account'))
        if not analytic.project_zone_id:
            raise UserError(
                _('The analytic account %s '
                  'does not have a Project Zone') % analytic.name
            )
        if not analytic.project_process_id:
            raise UserError(
                _('The analytic account %s '
                  'does not have a Project Process') % analytic.name
            )
        if not analytic.project_market_id:
            raise UserError(
                _('The analytic account %s '
                  'does not have a Project Market') % analytic.name
            )
        values.update({
            'project_zone_id': analytic.project_zone_id.id,
            'project_process_id': analytic.project_process_id.id,
            'project_market_id': analytic.project_market_id.id,
            'sales_condition': base64.encodestring(
                'Intercompany sales conditions.'
            ),
            'sales_condition_filename': 'intercompany.txt',
            'engineering_validation_id': 1,
            'process_validation_id': 1,
            'system_validation_id': 1,
            'force_project_name': analytic.name,
            }
        )
        return values
