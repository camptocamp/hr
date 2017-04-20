# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    opp_nda_ids = fields.One2many(
        'crm.lead',
        'cust_nda_id',
        string='Opportunities',
        domain=[('type', '=', 'opportunity')],
        compute='_compute_opp_nda',
        readonly=True,
    )
    customer_license_ids = fields.One2many(
        'res.partner.license',
        'partner_id',
        string='Licenses',
    )

    def _compute_opp_nda(self):
        for cust in self:
            domain = [('cust_nda_id', '=', cust.id),
                      ('domain', '!=', False),
                      ('start_date', '!=', False),
                      ('end_date', '!=', False)]
            nda_ids = self.env['crm.lead'].search(domain)
            for nda_id in nda_ids:
                cust.opp_nda_ids |= nda_id


class ResPartnerLicense(models.Model):
    _name = 'res.partner.license'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    license_type = fields.Selection([
        ('dev', _('Dev')),
        ('production', _('Production')),
        ('test_demo', _('Test / Demo')),
        ('dev_prod_opt', _('Dev + Production Option')),
    ])
    start_date = fields.Date(
        string='Start Date',
    )
    end_date = fields.Date(
        string='End Date',
    )
    area = fields.Char(
        string='Area',
    )
    domain = fields.Char(
        string='Domain',
    )
    license_comment = fields.Text(
        string='Comments',
    )
