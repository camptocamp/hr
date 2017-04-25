# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_intercompany_rules(ctx):
    warehouse = ctx.env['stock.warehouse']
    holding = ctx.env.ref('__setup__.roctool_holding')
    for company in ctx.env['res.company'].search([('id', '!=', holding.id)]):
        warehouse_id = warehouse.search([('company_id', '=', company.id)])[0]
        vals = {
            'so_from_po': True,
            'po_from_so': True,
            'warehouse_id': warehouse_id.id,
        }
        company.write(vals)


@anthem.log
def main(ctx):
    """ Main: creating intercompany rules """
    set_intercompany_rules(ctx)
