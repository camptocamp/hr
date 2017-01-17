# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def create_sales_team(ctx):
    companies = ['base.main_company',
                 'scen.company_fr',
                 'scen.company_gb',
                 'scen.company_lu',
                 'scen.company_us',
                 'scen.company_bpo'
                 ]
    for company in companies:
        company_name = ctx.env.ref(company).name
        xml_id = 'BSO_crm_team.%s' % company.split('.')[1]
        values = {'name': company_name,
                  'company_id': False,
                  'stage_ids': [(5, 0)]}
        create_or_update(ctx, 'crm.team', xml_id, values)


@anthem.log
def import_crm_stages(ctx):
    """ import CRM stages """

    content = resource_stream(req, 'data/install/crm_stage.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')


@anthem.log
def add_stage_to_sale_team(ctx):
    for s_team in ctx.env['crm.team'].search([]):
        s_team.stage_ids = (
            ctx.env['crm.stage'].search([]).ids
        )


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    create_sales_team(ctx)
    import_crm_stages(ctx)
    add_stage_to_sale_team(ctx)
