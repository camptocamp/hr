# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def configure_expense_products(ctx):
    """ set sale_ok and purchase_ok to False for expense products"""
    ctx.env['product.template'].search(
        [('can_be_expensed', '=', 'True')]
    ).write(
        {'sale_ok': False, 'purchase_ok': False}
    )


@anthem.log
def main(ctx):
    """ configure products """
    configure_expense_products(ctx)
