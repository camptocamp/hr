# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from anthem.lyrics.records import create_or_update
import anthem


@anthem.log
def configure_backend(ctx):
    """ Configure JIRA Backend"""
    xmlid = '__setup__.backend_jira_main'
    values = {
        'name': 'JIRA',
        'company_id': ctx.env.ref('base.main_company').id,
        'version': '7.2.0',
        'location': '',
    }
    create_or_update(ctx, 'jira.backend', xmlid, values)


@anthem.log
def main(ctx):
    """ Configuring JIRA Connector """
    configure_backend(ctx)
