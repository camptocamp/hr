# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import Requirement, resource_stream
from anthem.lyrics.loaders import load_csv_stream

req = Requirement.parse('roctool-odoo')


def load_csv(ctx, path, model, delimiter=','):
    content = resource_stream(req, path)
    load_csv_stream(ctx, model, content, delimiter=delimiter)


def load_users_csv(ctx, path, delimiter=','):
    # make sure we don't send any email
    model = ctx.env['res.users'].with_context({
        'no_reset_password': True,
        'tracking_disable': True,
    })
    load_csv(ctx, path, model, delimiter=delimiter)
