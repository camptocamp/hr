# -*- coding: utf-8 -*-
import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module(ctx):
    """Uninstall module 'bso_sales_forecast'"""
    uninstall(ctx, ['bso_sales_forecast'])


@anthem.log
def main(ctx):
    """Applying update 10.48.0"""
    uninstall_module(ctx)
