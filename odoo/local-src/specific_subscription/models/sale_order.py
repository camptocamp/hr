# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.subscription_id:
                vals = {
                    'project_zone_id': order.project_zone_id.id,
                    'project_process_id': order.project_process_id.id,
                    'project_market_id': order.project_market_id.id,
                    'sales_condition': order.sales_condition,
                    'sales_condition_filename': order.sales_condition_filename,
                }
                order.subscription_id.write(vals)
        return res
