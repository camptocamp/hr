# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def base_setup(ctx):
    """ Configure multicompany """
    general_settings = ctx.env['base.config.settings']
    vals = {'group_multi_company': True,
            'module_inter_company_rules': True}
    general_settings.create(vals).execute()


@anthem.log
def configure_companies(ctx):
    wh_obj = ctx.env['stock.warehouse']
    for company in ctx.env['res.company'].search([]):
        company.write({'so_from_po': True,
                       'po_from_so': True,
                       'auto_validation': True,
                       'warehouse_id': wh_obj.search(
                           [('company_id', '=', company.id)],
                           limit=1).id
                       })


@anthem.log
def main(ctx):
    """ Configuring intercompany rules """
    base_setup(ctx)
    configure_companies(ctx)
