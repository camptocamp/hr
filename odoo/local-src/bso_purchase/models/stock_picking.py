# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for picking in self:
            po = picking.purchase_id
            if po and po.has_subscription and not po.subscr_date_start:
                po.subscr_date_start = picking.date_done
                po.onchange_subscr()
        return res
