# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update
from . import bso_vars


@anthem.log
def setup_wh_companies(ctx):
    for company_id in bso_vars.coa_dict:
        if company_id != 'base.main_company':
            company = ctx.env.ref(company_id)
            vals = {'company_id': company.id,
                    'name': company.name,
                    'code': 'WH%s' % company.country_id.code,
                    }
            xml_id = '__setup__.wh_%s' % company_id.split('.')[1]
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
    """ Configuring intercompany rules """
    setup_wh_companies(ctx)
    setup_wh_pop(ctx)
