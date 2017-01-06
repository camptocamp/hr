# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from base64 import b64encode
from pkg_resources import resource_string

import anthem

from anthem.lyrics.records import create_or_update

from ..common import req


@anthem.log
def setup_company(ctx):
    """ Setup company """
    company = ctx.env.ref('base.main_company')
    company.name = 'RocTool'

    # load logo on company
    logo_content = resource_string(req, 'data/images/company_main_logo.jpg')
    b64_logo = b64encode(logo_content)
    company.logo = b64_logo

    with ctx.log(u'Configuring company'):
        values = {
            'name': "Roctool",
            'street': "",
            'zip': "",
            'city': "",
            'country_id': ctx.env.ref('base.fr').id,
            'phone': "+33 00 000 00 00",
            'fax': "+33 00 000 00 00",
            'email': "contact@roctool.fr",
            'website': "http://www.roctool.com",
            'vat': "EU-VAT",
            # 'parent_id': company.id,
            'logo': b64_logo,
            'currency_id': ctx.env.ref('base.EUR').id,
        }
        create_or_update(ctx, 'res.company',
                         'base.main_company',
                         values)


@anthem.log
def setup_language(ctx):
    """ Installing language and configuring locale formatting """
    for code in ('fr_FR',):
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
    setup_company(ctx)
    setup_language(ctx)
    set_web_base_url(ctx)
