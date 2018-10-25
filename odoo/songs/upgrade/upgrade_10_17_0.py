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
