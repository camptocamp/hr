# -*- coding: utf-8 -*-
# Author: Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import fields, models
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _load_win_action(self, act, **kw):
        act = self.env.ref(act)
        action = act.copy_data()[0]
        action['context'] = self._context.copy()
        action.update(kw)
        return action

    @api.multi
    def action_procure(self):
        action = self._load_win_action(
            'sale_purchase_sourcing.act_wiz_sale_order_source')
        action['context']['default_order_id'] = self.id
        return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sourcing_purchase_line_id = fields.Many2one(
        string='Sourcing purchase order line',
        comodel_name='purchase.order.line',
        readonly=True,
        ondelete='set null',
    )
