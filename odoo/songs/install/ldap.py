# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def create_ldap_entries(ctx):
    """ Configuring ldap """

    company = ctx.env.ref('base.main_company')
    ldap_template_user = ctx.env.ref('scen.ldap_template_user')
    ctx.env['res.company.ldap'].create({
        'ldap_server': '10.234.230.11',
        'ldap_server_port': 389,
        'ldap_tls': 0,
        'ldap_binddn': 'CN=Read AD,OU=SERVICES_ACCOUNTS,DC=carinae,DC=group',
        'ldap_password': 'HVNpY4Qw',
        'ldap_base': 'OU=USERS,OU=CARINAE,DC=carinae,DC=group',
        'ldap_filter': '(&(sAMAccountName=%s)(activate=TRUE))',
        'company': company.id,
        'user': ldap_template_user.id,
    })


@anthem.log
def remove_ldap_user_employee(ctx):
    """  """
    ldap_template_user = ctx.env.ref('scen.ldap_template_user')
    ctx.env['hr.employee'].search(
        [('user_id', '=', ldap_template_user.id)]).unlink()


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    # setup_company(ctx)
    create_ldap_entries(ctx)
    remove_ldap_user_employee(ctx)
