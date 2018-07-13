# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def create_default_exchange_backend(ctx):
    """
    create default exchange connector backend
    assign it to every user
    """
    xml_id = '__setup__.BSO_exchange_backend'
    values = {
        'name': 'TEST Exchange Backend',
        'version': 'exchange_2010',
        'location': 'dummy',
        'username': 'dummy',
        'password': 'dummy',
    }
    ex_back = create_or_update(ctx, 'exchange.backend', xml_id, values)
    ctx.env['res.users'].search([]).write({'default_backend': ex_back.id})


@anthem.log
def main(ctx):
    create_default_exchange_backend(ctx)
