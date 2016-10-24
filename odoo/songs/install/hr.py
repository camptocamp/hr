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
def import_hr_department1(ctx):
    content = resource_stream(req, 'data/install/hr_department1.csv')
    load_csv_stream(ctx, 'hr.department', content, delimiter=',')


@anthem.log
def import_hr_employee1(ctx):
    content = resource_stream(req, 'data/install/hr_employee1.csv')
    load_csv_stream(ctx, 'hr.employee', content, delimiter=',')


@anthem.log
def import_partner_employee_home_address(ctx):
    content = resource_stream(
        req,
        'data/install/res_partner_employee_home_address.csv')
    load_csv_stream(ctx, 'res.partner', content, delimiter=',')


@anthem.log
def import_hr_department2(ctx):
    content = resource_stream(req, 'data/install/hr_department2.csv')
    load_csv_stream(ctx, 'hr.department', content, delimiter=',')


@anthem.log
def import_hr_employee2(ctx):
    content = resource_stream(req, 'data/install/hr_employee_manager.csv')
    load_csv_stream(ctx, 'hr.employee', content, delimiter=',')


@anthem.log
def import_employee_family(ctx):
    content = resource_stream(req, 'data/install/hr_employee_family.csv')
    load_csv_stream(ctx, 'hr.employee.family', content, delimiter=',')


@anthem.log
def import_syntec_position(ctx):
    content = resource_stream(req, 'data/install/hr_syntec_position.csv')
    load_csv_stream(ctx, 'hr.syntec.position', content, delimiter=',')


@anthem.log
def import_contract_category(ctx):
    content = resource_stream(req, 'data/install/hr_contract_category.csv')
    load_csv_stream(ctx, 'hr.contract.category', content, delimiter=',')


@anthem.log
def create_expense_journal(ctx):
    """ for each company, create an 'Expense' journal """
    account_journal = ctx.env['account.journal']
    for company in ctx.env['res.company'].search([]):
        if not account_journal.search([('code', '=', 'EXP'),
                                       ('type', '=', 'purchase'),
                                       ('company_id', '=', company.id)]):
            values = {'name': 'Expense (%s)' % company.name,
                      'code': 'EXP',
                      'type': 'purchase',
                      'company_id': company.id
                      }
            account_journal.create(values)


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    create_expense_journal(ctx)
    import_hr_job(ctx)
    import_hr_department1(ctx)
    import_partner_employee_home_address(ctx)
    import_hr_employee1(ctx)
    import_hr_department2(ctx)
    import_hr_employee2(ctx)
    import_employee_family(ctx)
    import_syntec_position(ctx)
    import_contract_category(ctx)
    # import_employee_family_rel(ctx)
