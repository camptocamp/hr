# -*- coding: utf-8 -*-


def rename_crm_stage5(ctx):
    ctx.env.ref('__setup__.crm_stage_quote').name = '5- Proposal / Quote / JDA'


def pre(ctx):
    """ Pre-update """
    rename_crm_stage5(ctx)
