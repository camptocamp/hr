# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def uninstall_module(ctx):
    """Uninstall module 'sale_purchase_sourcing'"""
    uninstall(ctx, ['sale_purchase_sourcing'])


@anthem.log
def main(ctx):
    """Applying update 10.3.7"""
    uninstall_module(ctx)
