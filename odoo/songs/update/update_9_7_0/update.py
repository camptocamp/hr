# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem

from ...install.sale import configure_sale_double_validation


@anthem.log
def create_incoming_mail_server(ctx):
    ctx.env['fetchmail.server'].create({'name': 'Incoming mail server'})


@anthem.log
def main(ctx):
    """ Applying update 9.7.0 """
    create_incoming_mail_server(ctx)
    configure_sale_double_validation(ctx)
