# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


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

    def _compute_opp_nda(self):
        for cust in self:
            domain = [('cust_nda_id', '=', cust.id),
                      ('domain', '!=', False),
                      ('start_date', '!=', False),
                      ('end_date', '!=', False)]
            nda_ids = self.env['crm.lead'].search(domain)
            for nda_id in nda_ids:
                cust.opp_nda_ids |= nda_id
