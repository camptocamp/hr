# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream

from ...common import req


@anthem.log
def update_server_actions(ctx):
    content = resource_stream(req,
                              'data/upgrade/10_0_12/ir.actions.server.csv')
    load_csv_stream(ctx, 'ir.actions.server', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Main: Updating ir.action.server """
    update_server_actions(ctx)
