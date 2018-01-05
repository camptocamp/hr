# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream
import os

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def clean_views(ctx):
    """
    """
    query = (
        "delete from ir_ui_view where id in ("
        "select res_id from ir_model_data where "
        "model='ir.ui.view' and module='specific_product');")
    ctx.env.cr.execute(query)
    query = (
        "delete from ir_model_data where model='ir.ui.view' "
        "and module='specific_product';")
    ctx.env.cr.execute(query)


@anthem.log
def correct_logistics_routes(ctx):
    if os.environ.get('RUNNING_ENV') == 'prod':
        content = resource_stream(req, 'data/upgrade/stock.location.route.csv')
        load_csv_stream(ctx, 'stock.location.route', content, delimiter=',')


@anthem.log
def main(ctx):
    clean_views(ctx)
#    correct_logistics_routes(ctx)
