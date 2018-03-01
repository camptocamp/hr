# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    name = fields.Char(default='/')

    @api.multi
    def name_get(self):
        """ We want to have only the name field in the get name. """
        res = []
        for analytic in self:
            res.append((analytic.id, analytic.name))
        return res

    @api.model
    def create(self, vals):
        result = super(AccountAnalyticAccount, self).create(vals)

        if result.name == '/':
            result.generate_name()

        return result

    def generate_name(self):
        self.ensure_one()

        company_country_code = self.company_id.partner_id.country_id.code
        ref_partner = self.company_id.partner_id.ref
        ref_commercial_partner = self.partner_id.commercial_partner_id.ref
        glob_sec_share_by_companies = self.env['ir.sequence'].next_by_code(
            'end.name.account.analytic.account'
        )
        if not company_country_code:
            raise ValidationError(
                _('No country defined for partner %s') %
                self.company_id.partner_id.name
            )
        if not ref_partner:
            raise ValidationError(
                _('No internal reference specified on partner %s') %
                self.company_id.partner_id.name
            )
        if not ref_commercial_partner:
            raise ValidationError(
                _('No internal reference specified on partner %s') %
                self.partner_id.commercial_partner_id.name
            )
        if not glob_sec_share_by_companies:
            raise ValidationError(_(
                'Sequence undefined: End name of Account analytic account'
            ))
        self.name = "%s%s/%s/%s" % (
            company_country_code,
            ref_partner[-3:],
            ref_commercial_partner,
            glob_sec_share_by_companies
        )
