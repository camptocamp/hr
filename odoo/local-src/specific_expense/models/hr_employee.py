# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    expense_refund_account_id = fields.Many2one(
        'account.account',
        string='Expense Refund Account',
        related='address_home_id.property_account_payable_id',
        store=False,
        readonly=False,
    )

    @api.model
    def create(self, vals):
        if vals.get('address_home_id'):
            return super(Employee, self).create(vals)
        country_id = vals.get('country_id')
        if not country_id:
            Company = self.env['res.company']
            country_id = Company.browse(vals['company_id']).country_id.id
        Partner = self.env['res.partner']
        category_id = self.env.ref('specific_expense.employee_home').id
        vals_address = {
            'name': vals.get('name'),
            'supplier': True,
            'customer': False,
            'country_id': country_id,
            'category_id': [(4, category_id)],
        }
        partner = Partner.create(vals_address)
        vals['address_home_id'] = partner.id
        return super(Employee, self).create(vals)
