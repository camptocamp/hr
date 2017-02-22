# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from . import bso_vars
from anthem.lyrics.records import create_or_update


@anthem.log
def configure_chart_of_account(ctx):
    """Configure COA for companies"""
    account_settings = ctx.env['account.config.settings']

    for company_xml_id, coa in bso_vars.coa_dict.iteritems():
        company = ctx.env.ref(company_xml_id)
        with ctx.log("Import basic CoA for %s:" % company.name):
            vals = {'group_analytic_account_for_purchases': True,
                    'group_analytic_account_for_sales': True,
                    'group_analytic_accounting': True,
                    'module_account_tax_cash_basis': True,
                    'company_id': company.id,
                    'chart_template_id': ctx.env.ref(coa).id,
                    }
            acs = account_settings.create(vals)
            acs.onchange_chart_template_id()
            acs.execute()


@anthem.log
def reset_main_company_chart(ctx):
    ctx.env.ref('base.main_company').reset_chart()


@anthem.log
def create_new_company_SC(ctx):
    values = {
        'name': "BSO Network Solutions SC",
        'street': "",
        'zip': "",
        'city': "",
        'country_id': ctx.env.ref('base.ie').id,
        'parent_id': ctx.env.ref('base.main_company').id,
        'currency_id': ctx.env.ref('base.EUR').id,
    }
    create_or_update(ctx, 'res.company', 'scen.company_irl_sc', values)


@anthem.log
def main(ctx):
    create_new_company_SC(ctx)
    main_coa = ctx.env.ref('base.main_company').chart_template_id
    if main_coa != ctx.env.ref(bso_vars.coa_dict['base.main_company']):
        reset_main_company_chart(ctx)
    configure_chart_of_account(ctx)
