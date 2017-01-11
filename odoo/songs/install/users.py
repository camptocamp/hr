# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def change_admin_language(ctx):
    """ Changing admin language """
    ctx.env.ref('base.user_root').lang = 'fr_FR'


@anthem.log
def admin_user_password(ctx):
    # password for the test server,
    # the password must be changed in production
    ctx.env.user.password_crypt = (
        '$pbkdf2-sha512$19000$4dwbI4SQMqZUKmWsVcqZEw$nwhdpl0.pEDJhyv70gPHuTLBd'
        'yA87U3cDazNfrSYrutdNSBR8kgR20RcdmXBymNUbTFnsPZlbXajjNOA3y0RxQ'
    )


@anthem.log
def import_users(ctx):
    """ Import users """
    content = resource_stream(req, 'data/install/res.users.csv')
    load_csv_stream(ctx, 'res.users', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products """
    change_admin_language(ctx)
    admin_user_password(ctx)
    # import_users(ctx)
