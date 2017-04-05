# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def configure_sale_app(ctx):
    """Configure sale app"""

    sale_settings = ctx.env['sale.config.settings']
    sale_settings.create({
        # 'default_invoice_policy': 'delivery',
        # 'group_sale_delivery_address': 1,
        # 'group_display_incoterms': 1,
        # 'group_discount_per_so_line': 1,
        'group_mrp_properties': 1,
        'group_product_pricelist': True,
        'group_sale_pricelist': True,
        'group_product_variant': 1,
        'group_uom': 1,
        'sale_pricelist_setting': 'formula',
    }).execute()


@anthem.log
def configure_sale_double_validation(ctx):
    company = ctx.env.ref('base.main_company')
    company.write({
        'so_double_validation': 'two_step',
        'so_double_validation_amount': 0.0,
    })


@anthem.log
def configure_contract_template(ctx):
    vals = {'name': 'Contract template',
            'type': 'template',
            'state': 'open'
            }
    xml_id = '__setup__.subscription_tmpl_1'
    create_or_update(ctx, 'sale.subscription', xml_id, vals)

    sale_tmpl = ctx.env.ref('website_quote.website_quote_template_default')
    sale_tmpl.contract_template = ctx.env.ref(xml_id).id


@anthem.log
def main(ctx):
    """ Configuring sales """
    # activate_multicurrency(ctx)
    configure_sale_app(ctx)
    # TODO v10: this in v9 were in a `pre` step.
    # Is really needed to execute them before?
    configure_sale_double_validation(ctx)
    configure_contract_template(ctx)
