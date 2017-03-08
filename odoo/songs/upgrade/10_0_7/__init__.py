# -*- coding: utf-8 -*-

import anthem


@anthem.log
def activate_sale_layout(ctx):
    """ Activate sale layout """
    sale_settings = ctx.env['sale.config.settings']
    sale_settings.create({'group_sale_layout': 1}).execute()


def post(ctx):
    """ Post-update """
    activate_sale_layout(ctx)


def rename_crm_stage5(ctx):
    ctx.env.ref('__setup__.crm_stage_quote').name = '5- Proposal / Quote / JDA'


def pre(ctx):
    """ Pre-update """
    rename_crm_stage5(ctx)
