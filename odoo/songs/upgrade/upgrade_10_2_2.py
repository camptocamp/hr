# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def fix_timesheets_groups(ctx):
    employee_group = ctx.env.ref("base.group_user")
    timesheets_menu = ctx.env.ref("hr_timesheet.timesheet_menu_root")

    if timesheets_menu not in employee_group.menu_access:
        employee_group.menu_access += timesheets_menu


@anthem.log
def main(ctx):
    fix_timesheets_groups(ctx)
