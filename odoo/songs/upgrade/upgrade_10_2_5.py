# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


def activate_intercompany(ctx, company):
    wh_obj = ctx.env['stock.warehouse']
    with ctx.log("Configuring intercompany rules "
                 "for company %s:" % company.name):
        company.write({'so_from_po': True,
                       'po_from_so': True,
                       'auto_validation': False,
                       'auto_generate_invoices': False,
                       'warehouse_id': wh_obj.search(
                           [('company_id', '=', company.id),
                            ('code', 'like', 'WH')],
                           limit=1).id
                       })


@anthem.log
def configure_companies(ctx):
    company = ctx.env.ref('base.main_company')
    activate_intercompany(ctx, company)
    company = ctx.env['res.company'].search([('name', '=', 'BSO SC')], limit=1)
    if company:
        activate_intercompany(ctx, company)


@anthem.log
def main(ctx):
    """ Main: intercompany configuration """
    configure_companies(ctx)
