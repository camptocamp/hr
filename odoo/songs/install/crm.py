# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def import_crm_stages(ctx):
    """ import CRM stages """

    content = resource_stream(req, 'data/install/crm_stage.csv')
    load_csv_stream(ctx, 'crm.stage', content, delimiter=',')


@anthem.log
def add_stage_to_sale_team(ctx):
    ctx.env['crm.team'].search([]).stage_ids = (
        ctx.env['crm.stage'].search([]).ids
    )


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    import_crm_stages(ctx)
    add_stage_to_sale_team(ctx)
