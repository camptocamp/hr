# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_po_double_validation(ctx):
    purchase_settings = ctx.env['purchase.config.settings']
    # Activate lots and serial nuimber
    purchase_settings.create({'po_double_validation': 'two_step'}).execute()


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    set_po_double_validation(ctx)
