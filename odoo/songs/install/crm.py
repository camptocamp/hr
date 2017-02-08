# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream
from ..common import req
from . import roctool_vars


@anthem.log
def import_crm_stages(ctx):
    """ import CRM stages """

    content = resource_stream(req, 'data/install/crm.stage.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')


@anthem.log
def import_crm_activities(ctx):
    content = resource_stream(req, 'data/install/crm.activity.base.csv')
    load_csv_stream(ctx, 'crm.activity', content, delimiter=',')
    content = resource_stream(req, 'data/install/crm.activity.links.csv')
    load_csv_stream(ctx, 'crm.activity', content, delimiter=',')


@anthem.log
def create_sales_team(ctx):
    """ create one Sales Team per company """
    # first deactivate existing one coming from sales_team module
    ctx.env.ref('sales_team.team_sales_department').active = False
    ctx.env.ref('sales_team.salesteam_website_sales').active = False
    # then create the new ones
    for company in ctx.env['res.company'].search([]):
        xml_id = '__setup__.crm_team_%s' % company.id
        create_or_update(ctx, 'crm.team', xml_id, {'name': company.name,
                                                   'company_id': False})


@anthem.log
def add_stage_to_sale_team(ctx):
    for s_team in ctx.env['crm.team'].search([]):
        s_team.stage_ids = [ctx.env.ref(x).id for x in roctool_vars.crm_stages]


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    import_crm_stages(ctx)
    create_sales_team(ctx)
    add_stage_to_sale_team(ctx)
    import_crm_activities(ctx)
