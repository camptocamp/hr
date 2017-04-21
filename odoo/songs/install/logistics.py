# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update, add_xmlid
from . import bso_vars


@anthem.log
def activate_options(ctx):
    """ Activating logistics options """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids': [
            (4, ctx.env.ref('stock.group_production_lot').id),
            (4, ctx.env.ref('stock.group_stock_multi_locations').id),
            (4, ctx.env.ref('stock.group_stock_multi_warehouses').id),
            (4, ctx.env.ref('stock.group_adv_location').id)
        ]

    })


@anthem.log
def set_delivery_pick_ship(ctx):
    """ Setting pick-ship on the warehouse """
    ctx.env.ref('stock.warehouse0').delivery_steps = 'pick_ship'


@anthem.log
def setup_wh_companies(ctx):
    for company_id in bso_vars.coa_dict2:
        if company_id != 'base.main_company':
            company = ctx.env.ref(company_id)
            wh = ctx.env['stock.warehouse'].search(
                [('company_id', '=', company.id)]
            )
            vals = {'company_id': company.id,
                    'name': company.name,
                    'code': 'WH%s' % company.country_id.code,
                    }
            xml_id = '__setup__.wh_%s' % company_id.split('.')[1]
            if wh:
                add_xmlid(ctx, wh, xml_id)
            create_or_update(ctx, 'stock.warehouse', xml_id, vals)


@anthem.log
def setup_wh_pop(ctx):
    for pop in ctx.env['bso.network.pop'].search([]):
        with ctx.log("Creating WH for POP %s:" % pop.name):
            company = ctx.env.ref('base.main_company')
            vals = {'company_id': company.id,
                    'name': pop.name,
                    'code': '%s' % pop.name.replace('-', ''),
                    }
            xml_id = '__setup__.wh_pop_%s' % pop.id
            create_or_update(ctx, 'stock.warehouse', xml_id, vals)


@anthem.log
def main(ctx):
    """ Configuring logistics rules """
    activate_options(ctx)
    set_delivery_pick_ship(ctx)
    setup_wh_companies(ctx)
    # CAUTION: this will need to be run again after importing the POPs
    setup_wh_pop(ctx)
