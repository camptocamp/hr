# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def configure_sale_app(ctx):
    """Configure sale app"""

    sale_settings = ctx.env['sale.config.settings']

    vals = {
        # 'default_invoice_policy': 'delivery',
        # 'group_sale_delivery_address': 1,
        # 'group_display_incoterms': 1,
        # 'group_discount_per_so_line': 1,
        'group_mrp_properties': 1,
        'group_product_pricelist': True,
        'group_sale_pricelist': True,
        'sale_pricelist_setting': 'formula',
        }
    acs = sale_settings.create(vals)

    acs.execute()


@anthem.log
def configure_sale_double_validation(ctx):
    company = ctx.env.ref('base.main_company')
    company.write({
        'so_double_validation': 'two_step',
        'so_double_validation_amount': 0.0,
    })


@anthem.log
def main(ctx):
    """ Configuring sales """
    # activate_multicurrency(ctx)
    configure_sale_app(ctx)
    configure_sale_double_validation(ctx)
    # create_bank_accounts(ctx)
