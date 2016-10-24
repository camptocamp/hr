# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def base_setup(ctx):
    """ Configure multicompany """
    general_settings = ctx.env['base.config.settings']
    vals = {'group_light_multi_company': True,
            'module_inter_company_rules': False}
    general_settings.create(vals).execute()


@anthem.log
def main(ctx):
    base_setup(ctx)
