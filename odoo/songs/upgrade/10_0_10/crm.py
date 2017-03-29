# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ...common import req


@anthem.log
def import_filters(ctx):
    content = resource_stream(req, 'data/upgrade/10_0_4/ir.filters.csv')
    load_csv_stream(ctx, 'ir.filters', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Fix demo data """
    import_filters(ctx)
