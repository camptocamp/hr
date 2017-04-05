# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
# from . import bso_vars


@anthem.log
def setup_language(ctx):
    """ Installing language and configuring locale formatting """
    for code in ('fr_FR', 'es_ES'):
        ctx.env['base.language.install'].create({'lang': code}).lang_install()
    ctx.env['res.lang'].search([]).write({
        'grouping': [3, 0],
        'date_format': '%d/%m/%Y',
    })


@anthem.log
def set_web_base_url(ctx):
    """ Configuring web.base.url """
    url = 'http://localhost:8069'
    ctx.env['ir.config_parameter'].set_param('web.base.url', url)
    ctx.env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    # setup_company(ctx)
    setup_language(ctx)
    set_web_base_url(ctx)
