# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    project_zone_id = fields.Many2one(
        comodel_name='project.zone',
        string='Project Zone',
        required=True,
    )
    project_process_id = fields.Many2one(
        comodel_name='project.process',
        string='Project Process',
        required=True
    )
    project_market_id = fields.Many2one(
        comodel_name='project.market',
        string='Project Market',
        required=True
    )
    sales_condition = fields.Binary(
        string='Sales Conditions',
        required=True,
        attachment=True,
        copy=True,
    )
    sales_condition_filename = fields.Char()

    @api.multi
    def _prepare_renewal_order_values(self):
        res = super(SaleSubscription, self)._prepare_renewal_order_values()
        for contract in self:
            vals = {
                'project_zone_id': contract.project_zone_id.id,
                'project_process_id': contract.project_process_id.id,
                'project_market_id': contract.project_market_id.id,
                'sales_condition': contract.sales_condition,
                'sales_condition_filename': contract.sales_condition_filename,
            }
            res[contract.id].update(vals)
        return res
