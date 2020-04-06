# -*- coding: utf-8 -*-
import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module(ctx):
    """Uninstall module 'bso_opportunities_reporiting'"""
    uninstall(ctx, ['bso_opportunities_reporiting'])


@anthem.log
def main(ctx):
    """Applying update 10.35.1"""
    uninstall_module(ctx)
