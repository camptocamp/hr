# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from songs.install.crm import disable_sales_teams


@anthem.log
def main(ctx):
    """ Upgrade 10.1.4 """
    disable_sales_teams(ctx)
