# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream
import anthem
from ..common import req
from anthem.lyrics.loaders import load_csv_stream


@anthem.log
def setup_product_uom_category(ctx):
    """ Setup product uom category """
    content = resource_stream(req, 'data/install/product_uom_categ.csv')
    load_csv_stream(ctx, 'product.uom.categ', content, delimiter=',')


@anthem.log
def setup_product_uom(ctx):
    """ Setup product uom """
    content = resource_stream(req, 'data/install/product_uom.csv')
    load_csv_stream(ctx, 'product.uom', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Upgrade 10.2.0 """
    setup_product_uom_category(ctx)
    setup_product_uom(ctx)
