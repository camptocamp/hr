# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem


@anthem.log
def compute_generate_lead(ctx):
    """set generate_lead to true for partners with a lead"""
    Lead = ctx.env['crm.lead']
    leads = Lead.search([('type', '=', 'lead')])
    leads.mapped('partner_id').write({'generate_lead': True})


@anthem.log
def fix_property_product_pricelist(ctx):
    field = ctx.env['ir.model.fields'].search(
        [('model', '=', 'res.partner'),
         ('name', '=', 'property_product_pricelist'),
         ]
    )
    props = ctx.env['ir.property'].search(
        [('name', '=', 'property_product_pricelist'),
         ('res_id', '=', False),
         ('fields_id', '=', field.id),
         ]
    )
    props.unlink()


@anthem.log
def main(ctx):
    compute_generate_lead(ctx)
    fix_property_product_pricelist(ctx)
