# -*- coding: utf-8 -*-
# © 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem


# for their test instance (hosted by them),
# we don't want email to be sent to the real customers.
# But they want to test this mail functionnality

@anthem.log
def replace_partner_email(ctx):
    records = ctx.env['res.partner'].search([])

    records.write({
        'email': 'mailusertest@bsonetwork.com'
    })


@anthem.log
def replace_employee_email(ctx):
    records = ctx.env['hr.employee'].search([])

    records.write({
        'work_email': 'mailusertest@bsonetwork.com'
    })


@anthem.log
def create_incoming_mail_server(ctx):
    ctx.env['fetchmail.server'].create({'name': 'Incoming mail server'})


@anthem.log
def main(ctx):
    """ Replacing email addresses """
    replace_partner_email(ctx)
    replace_employee_email(ctx)
    create_incoming_mail_server(ctx)
