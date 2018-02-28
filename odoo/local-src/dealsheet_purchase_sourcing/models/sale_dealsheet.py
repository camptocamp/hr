# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class SaleDealsheet(models.Model):

    _inherit = 'sale.dealsheet'

    def _load_win_action(self, act, **kw):
        act = self.env.ref(act)
        action = act.copy_data()[0]
        action['context'] = self._context.copy()
        action.update(kw)
        return action

    @api.multi
    def action_procure(self):
        action = self._load_win_action(
            'bso_dealsheet.act_wiz_sale_dealsheet_source')
        action['context']['default_dealsheet_id'] = self.id
        return action


class SaleDealsheetLine(models.Model):

    _inherit = 'sale.dealsheet.line'

    duration = fields.Integer(
        related='dealsheet_id.duration',
        readonly=True,
        store=False
    )
    sourcing_purchase_line_id = fields.Many2one(
        string='Sourcing purchase order line',
        comodel_name='purchase.order.line',
        readonly=True,
        ondelete='set null',
    )
