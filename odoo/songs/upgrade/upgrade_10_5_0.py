# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem
from anthem.lyrics.modules import uninstall


@anthem.log
def main(ctx):
    uninstall(ctx, ['sale_margin', 'sale_line_cost_control'])
