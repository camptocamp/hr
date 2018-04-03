# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    def _prepare_sale_order_data(self, name, partner, company,
                                 direct_delivery_address):
        values = super(PurchaseOrder, self)._prepare_sale_order_data(
            name, partner, company, direct_delivery_address
        )[0]
        analytic = self.mapped('order_line.account_analytic_id')
        if analytic:
            analytic_account = analytic[0]
        else:
            analytic_account = analytic
        # if len(analytic) != 1:
        #     raise UserError(_('All the lines of the purchase must '
        #                       'be on the same analytic account'))
        values.update({
            'project_id': analytic_account.id,
            }
        )
        return values
