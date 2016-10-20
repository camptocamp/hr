# -*- coding: utf-8 -*-
# © 2016 Camptocamp (alexandre.fayolle@camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_variable = fields.Float(
        'Variable wage', digits=(16, 2)
    )
    bonus_exceptional = fields.Float(
        'Exceptional bonus', digits=(16, 2),
        track_visibility='onchange',
    )
    bonus_target_based = fields.Float(
        'Target-based bonus', digits=(16, 2),
        track_visibility='onchange',
    )
    wage_package = fields.Float(
        'Package', digits=(16, 2), compute='_get_wage_package', store=True
    )
    wage_raise = fields.Float(
        'Raise', digits=(16, 2), compute='_get_wage_raise', store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='employee_id.company_id.currency_id',
        store=True,
        readonly=True
    )
    previous_contract_id = fields.Many2one(
        'hr.contract',
        string='Previous contract',
        store=True,
        readonly=True,
        compute='_get_previous_contract'
    )

    @api.depends('wage', 'wage_variable')
    def _get_wage_package(self):
        for rec in self:
            rec.wage_package = rec.wage + (rec.wage_variable or 0)

    @api.depends('employee_id.contract_ids.date_end', 'date_start')
    def _get_previous_contract(self):
        for rec in self:
            rec.previous_contract_id = self.search(
                [('employee_id', '=', rec.employee_id.id),
                 ('date_end', '<=', rec.date_start),
                 ],
                order='date_end DESC',
                limit=1)

    @api.depends('previous_contract_id.wage_package',
                 'previous_contract_id.bonus_exceptional',
                 'wage_package',
                 'bonus_exceptional')
    def _get_wage_raise(self):
        for rec in self:
            if rec.previous_contract_id:
                rec.wage_raise = (rec.wage_package +
                                  rec.bonus_exceptional -
                                  rec.previous_contract_id.wage_package -
                                  rec.previous_contract_id.bonus_exceptional)
            else:
                rec.wage_raise = 0
