# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream
from ...common import req


@anthem.log
def import_filters(ctx):
    content = resource_stream(req, 'data/upgrade/10_0_4/ir.filters.csv')
    load_csv_stream(ctx, 'ir.filters', content, delimiter=',')


@anthem.log
def import_server_actions(ctx):
    content = resource_stream(req, 'data/upgrade/10_0_4/ir.actions.server.csv')
    load_csv_stream(ctx, 'ir.actions.server', content, delimiter=',')


@anthem.log
def import_action_rule(ctx):
    content = resource_stream(req, 'data/upgrade/10_0_4/base.action.rule.csv')
    load_csv_stream(ctx, 'base.action.rule', content, delimiter=',')


@anthem.log
def create_base_action_rules(ctx):
    lead_model = ctx.env['ir.model'].search([('model', '=', 'crm.lead')],
                                            limit=1)
    bar = {
        '__setup__.bar_crm_lead_3_arrival': {
            'active': True,
            'model_id': lead_model.id,
            'sequence': 1,
            'name': 'cannot go to collect information state',
            'kind': 'on_write',
            'filter_pre_id': ctx.env.ref('__setup__.filter_crm_lead_1_2').id,
            'filter_pre_domain': "['|',('stage_id.name', 'ilike', '1'),"
                                 "('stage_id.name', 'ilike', '2')]",
            'filter_id':  ctx.env.ref('__setup__.filter_crm_lead_3').id,
            'filter_domain': "[('stage_id.name', 'ilike', '3')]",
            'server_action_ids': [
                (4, ctx.env.ref(
                    '__setup__.server_action_crm_lead_check_3_arrival').id)],
        },
        '__setup__.bar_crm_lead_4_arrival': {
            'active': True,
            'model_id': lead_model.id,
            'sequence': 1,
            'name': 'cannot go to feasability state',
            'kind': 'on_write',
            'filter_pre_id': ctx.env.ref('__setup__.filter_crm_lead_3').id,
            'filter_pre_domain': "[('stage_id.name', 'ilike', '4')]",
            'filter_id': ctx.env.ref('__setup__.filter_crm_lead_4').id,
            'filter_domain': "[('stage_id.name', 'ilike', '4')]",
            'server_action_ids': [
                (4, ctx.env.ref(
                    '__setup__.server_action_crm_lead_check_4_arrival').id)],
        }
    }

    for k, v in bar.iteritems():
        create_or_update(ctx, 'base.action.rule', k, v)


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    import_filters(ctx)
    import_server_actions(ctx)
    # import_action_rule(ctx)
    create_base_action_rules(ctx)
