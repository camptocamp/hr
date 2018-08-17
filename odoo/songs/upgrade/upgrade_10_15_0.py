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
def main(ctx):
    compute_generate_lead(ctx)
