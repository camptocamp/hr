# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    opp_nda_ids = fields.Many2many(
        'crm.lead',
        string='NDAs',
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
            domain = [('partner_id', '=', cust.id),
                      ('type', '=', 'opportunity'),
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
        required=True,
        index=True,
    )
    license_type = fields.Selection(
        [('dev', 'Dev'),
         ('production', 'Production'),
         ('test_demo', 'Test / Demo'),
         ('dev_prod_opt', 'Dev + Production Option')],
        required=True,
    )
    start_date = fields.Date(
        string='Start Date',
        required=True,
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
