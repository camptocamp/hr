# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from pkg_resources import resource_stream

import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def import_hr_job(ctx):
    content = resource_stream(req, 'data/install/hr_job.csv')
    load_csv_stream(ctx, 'hr.job', content, delimiter=',')


@anthem.log
def import_hr_employee_categ(ctx):
    content = resource_stream(req, 'data/install/hr_employee_category.csv')
    load_csv_stream(ctx, 'hr.employee.category', content, delimiter=',')


@anthem.log
def import_hr_department1(ctx):
    content = resource_stream(req, 'data/install/hr_department1.csv')
    load_csv_stream(ctx, 'hr.department', content, delimiter=',')


@anthem.log
def import_hr_employee1(ctx):
    content = resource_stream(req, 'data/install/hr_employee2.csv')
    load_csv_stream(ctx, 'hr.employee', content, delimiter=',')


@anthem.log
def import_partner_employee_home_address(ctx):
    content = resource_stream(
        req,
        'data/install/res_partner_employee_home_address.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


# @anthem.log
# def import_hr_department2(ctx):
#     content = resource_stream(req, 'data/install/product_expense.csv')
#     load_csv_stream(ctx, 'product.product', content, delimiter=',')


# @anthem.log
# def import_hr_employee2(ctx):
#     content = resource_stream(req, 'data/install/res.users.ldap.csv')
#     load_csv_stream(ctx, 'res.users', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    import_hr_job(ctx)
    import_hr_employee_categ(ctx)
    import_hr_department1(ctx)
    import_partner_employee_home_address(ctx)
    import_hr_employee1(ctx)
    # import_hr_department2(ctx)
    # import_hr_employee2(ctx)
