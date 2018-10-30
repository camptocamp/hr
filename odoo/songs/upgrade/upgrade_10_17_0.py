# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def uninstall_base_dj(ctx):
    uninstall(
        ctx,
        ['base_dj',
         'dj_compilation_account',
         'dj_compilation_stock',
         ]
    )


@anthem.log
def main(ctx):
    uninstall_base_dj(ctx)


@anthem.log
def pre(ctx):
    drop_specific_crm_assets_view(ctx)


@anthem.log
def drop_specific_crm_assets_view(ctx):
    view = ctx.env.ref('specific_crm.assets_backend', raise_if_not_found=False)
    if view:
        view.unlink()
