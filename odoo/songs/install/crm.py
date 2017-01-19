# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def import_crm_stages(ctx):
    """ import CRM stages """

    content = resource_stream(req, 'data/install/crm.stage.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')


@anthem.log
def import_crm_activities(ctx):
    content = resource_stream(req, 'data/install/crm.activity.base.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')
    content = resource_stream(req, 'data/install/crm.activity.links.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')


@anthem.log
def add_stage_to_sale_team(ctx):
    for s_team in ctx.env['crm.team'].search([]):
        s_team.stage_ids = (
            ctx.env['crm.stage'].search([('name', 'in', [
                'Initial Demand',
                'NDA',
                'Information collection',
                'Feasibility Study',
                'GO / NOGO',
                'Commercial Offer',
                'Won',
                'Cancel',
            ])]).ids
        )


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    import_crm_stages(ctx)
    add_stage_to_sale_team(ctx)
    import_crm_activities(ctx)
