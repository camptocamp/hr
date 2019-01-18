# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem


@anthem.log
def post(ctx):
    so_lines = ctx.env['sale.order.line'].search(
        [('order_id.state', 'not in', ('draft', 'cancel'))]
    )
    so_lines._compute_qty_delivered_calculated()
