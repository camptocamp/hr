# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_zone_id = fields.Many2one(comodel_name='project.zone',
                                      required=True)
    project_process_id = fields.Many2one(comodel_name='project.process',
                                         required=True)
    project_market_id = fields.Many2one(comodel_name='project.market',
                                        required=True)

    def _generate_acc_name(self, use_existing_one=None):
        """
        generate an analytic account name according to the following structure:
            123ABCXXYYZZ with
                123: number autoincrement (use Odoo sequence)
                ABC: customer.ref field
                XX: Code of the project zone
                YY: Code of the project process
                ZZ: Code of the project market
        """
        if use_existing_one:
            return use_existing_one

        seq = self.env['ir.sequence'].next_by_code('project')
        return ''.join([seq,
                        self.partner_id.ref or "ABC",
                        self.project_zone_id.code,
                        self.project_process_id.code,
                        self.project_market_id.code,
                        ])

    @api.multi
    def _create_analytic_account(self, prefix=None):
        super(SaleOrder, self)._create_analytic_account(prefix=prefix)
        for order in self:
            name = order._generate_acc_name()
            order.project_id.name = name

    @api.onchange('opportunity_id')
    def onchange_opportunity_id(self):
        if self.opportunity_id:
            self.update({
                'project_zone_id': self.opportunity_id.project_zone_id.id,
                'project_process_id': (
                    self.opportunity_id.project_process_id.id
                ),
                'project_market_id': self.opportunity_id.project_market_id.id,
                })

    @api.onchange('order_line')
    def onchange_order_line(self):
        order_line = self.order_line
        option_lines = []
        for line in order_line:
            if line.product_id:
                for product in line.product_id.optional_product_ids:
                    if self.pricelist_id:
                        price = self.pricelist_id.with_context(
                            uom=product.uom_id.id).get_product_price(
                            product, 1, False)
                    else:
                        price = product.list_price
                    data = {
                        'product_id': product.id,
                        'name': product.name,
                        'quantity': 1,
                        'uom_id': product.uom_id.id,
                        'price_unit': price,
                        'discount': 0,
                    }
                    option_lines.append((0, 0, data))
        self.options = option_lines
