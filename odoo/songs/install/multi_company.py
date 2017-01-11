# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def activate_currencies(ctx, curr_list=['EUR']):
    curr_obj = ctx.env['res.currency']
    for curr in curr_list:
        curr_obj.with_context(
            active_test=False).search(
                [('name', '=', curr)], limit=1).active = True


@anthem.log
def import_companies(ctx):
    """ import company """

    content = resource_stream(req, 'data/install/res.company.csv')
    load_csv_stream(ctx, 'res.company', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    activate_currencies(ctx, ['GBP', 'EUR', 'USD', 'TWD', 'JPY', 'CNY'])
    import_companies(ctx)
