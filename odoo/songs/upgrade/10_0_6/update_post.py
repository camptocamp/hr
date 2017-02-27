# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_settings_production_lot(ctx):
    stock_settings = ctx.env['stock.config.settings']
    # Activate lots and serial nuimber
    stock_settings.create({'group_stock_production_lot': 1}).execute()


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    set_settings_production_lot(ctx)
