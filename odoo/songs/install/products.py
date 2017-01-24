# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pkg_resources import resource_stream
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def load_attributes(ctx):
    """ Import attributes """
    content = resource_stream(req, 'data/install/product.attribute.csv')
    load_csv_stream(ctx, 'product.attribute', content, delimiter=',')


@anthem.log
def load_attribute_values(ctx):
    """ Import attr values """
    content = resource_stream(req, 'data/install/product.attribute.values.csv')
    load_csv_stream(ctx, 'product.attribute.value', content, delimiter=',')


@anthem.log
def load_templates(ctx):
    """ Import templates """
    toto = ctx.env['product.template'].with_context(
        create_product_product=True)
    content = resource_stream(req, 'data/install/product.template.csv')
    load_csv_stream(ctx,
                    toto,
                    content, delimiter=',')


@anthem.log
def load_template_attributes(ctx):
    """ Import attr values """
    content = resource_stream(req, 'data/install/product.attribute.line.csv')
    load_csv_stream(ctx, 'product.attribute.line', content, delimiter=',')


@anthem.log
def load_product_product(ctx):
    """ populate products """
    content = resource_stream(req, 'data/install/product.product.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')
    content = resource_stream(req, 'data/install/product.product_others.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')
    content = resource_stream(req, 'data/install/product.product_service.csv')
    load_csv_stream(ctx, 'product.product', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products """
    load_attributes(ctx)
    load_attribute_values(ctx)
    load_templates(ctx)
    load_template_attributes(ctx)
    load_product_product(ctx)
