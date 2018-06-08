# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req

""" File for demo data

These songs will be called when the mode is 'demo', we should import only
excerpt of data, while the full data is only imported in the 'full' mode.

"""


@anthem.log
def import_customers(ctx):
    """ Importing customers from csv """
    content = resource_stream(req, 'data/sample/customers.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Loading demo data """
    import_customers(ctx)
