# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def pre(ctx):
    '''remove views from expensify and specific_hr'''
    ctx.env.cr.execute("DELETE FROM ir_ui_view "
                       "WHERE id IN "
                       "    (SELECT res_id "
                       "     FROM ir_model_data "
                       "     WHERE module IN ('expensify', 'specific_hr') "
                       "       AND model='ir.ui.view')"
                       )
