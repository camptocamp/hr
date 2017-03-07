# -*- coding: utf-8 -*-
# © 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem


@anthem.log
def replace_partner_email(ctx):
    records = ctx.env['res.partner'].search([])

    records.write({
        'email': 'mailusertest@bsonetwork.com'
    })


@anthem.log
def main(ctx):
    """ Replacing email addresses """
    replace_partner_email(ctx)
