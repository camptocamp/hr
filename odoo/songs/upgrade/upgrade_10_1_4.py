# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from songs.install.crm import disable_sales_teams


@anthem.log
def correct_names(ctx):
    general_settings = ctx.env['base.config.settings']
    conf = general_settings.get_default_partner_names_order([])
    order = conf['partner_names_order']
    if order == 'first_last':
        ctx.log_line('Names are already correct')
    else:
        with ctx.log('Correcting first names and last names'):
            vals = {'partner_names_order': 'first_last'}
            general_settings.create(vals).execute()

            partners = ctx.env['res.partner'].search([
                ('is_company', '=', False),
                ('firstname', '!=', False), ('lastname', '!=', False),
            ])
            ctx.env.cr.execute("""
                UPDATE res_partner SET
                firstname = lastname,
                lastname = firstname
                WHERE id IN %s
            """, (tuple(partners.ids),))


@anthem.log
def main(ctx):
    """ Upgrade 10.1.4 """
    correct_names(ctx)
    disable_sales_teams(ctx)
