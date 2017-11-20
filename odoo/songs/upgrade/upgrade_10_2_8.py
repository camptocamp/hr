# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def uninstall_module(ctx):
    """
    uninstall leaves_constraints and hr_date_validated
    """
    uninstall(ctx, ['leaves_constraints', 'hr_date_validated'])


@anthem.log
def main(ctx):
    uninstall_module(ctx)
