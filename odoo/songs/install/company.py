# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req
from . import bso_vars


@anthem.log
def base_setup(ctx):
    """ Configure multicompany """
    general_settings = ctx.env['base.config.settings']
    vals = {'group_light_multi_company': True,
            'module_inter_company_rules': True}
    general_settings.create(vals).execute()


@anthem.log
def setup_companies(ctx):
    """ Setup company """
    content = resource_stream(req, 'data/install/res.company.csv')
    load_csv_stream(ctx, 'res.company', content, delimiter=',')


@anthem.log
def configure_companies(ctx):
    wh_obj = ctx.env['stock.warehouse']
    for company_id in bso_vars.coa_dict:
        company = ctx.env.ref(company_id)
        with ctx.log("Configuring intercompany rules "
                     "for company %s:" % company.name):
            company.write({'so_from_po': True,
                           'po_from_so': True,
                           'auto_validation': False,
                           'warehouse_id': wh_obj.search(
                               [('company_id', '=', company.id),
                                ('code', 'like', 'WH')],
                               limit=1).id
                           })


@anthem.log
def main(ctx):
    """ Main: company data """
    base_setup(ctx)
    # TODO: currently broken:
    #  u"No matching record found for name 'GBP' in field 'Currency'"
    # setup_companies(ctx)
    # configure_companies(ctx)
