# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_zone_id = fields.Many2one(comodel_name='project.zone',
                                      required=True)
    project_process_id = fields.Many2one(comodel_name='project.process',
                                         required=True)
    project_market_id = fields.Many2one(comodel_name='project.market',
                                        required=True)

    engineering_validation_id = fields.Many2one(
        'res.users',
        string='Engineering Validation',
        track_visibility=True,
        copy=False,
        readonly=True,
    )
    system_validation_id = fields.Many2one(
        'res.users',
        string='System Validation',
        track_visibility=True,
        copy=False,
        readonly=True,
    )
    process_validation_id = fields.Many2one(
        'res.users',
        string='Process Validation',
        track_visibility=True,
        copy=False,
        readonly=True,
    )
    sales_condition = fields.Binary(
        string='Sales Condition',
        required=True,
        attachment=True,
        copy=True,
        states={'draft': [('required', False)],
                'cancel': [('required', False)]}
    )
    sales_condition_filename = fields.Char()

    @api.model
    def _setup_fields(self, partial):
        super(SaleOrder, self)._setup_fields(partial)
        selection = self._fields['state'].selection
        position = 0
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'draft':
                position = idx
            elif state == 'final_quote':
                exists = True
        if not exists:
            selection.insert(position + 1, ('final_quote', _('Final Quote')))

    def _generate_acc_name(self, use_existing_one=None):
        """ Generate analytic account name

        According to the following structure:
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

    @api.onchange('order_line', 'order_line.product_id')
    def onchange_order_line(self):
        order_line = self.order_line
        option_lines = []
        if order_line:
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

    @api.multi
    def _check_ghost(self):
        for so in self:
            ghost_prd = self.order_line.search_read(
                [('product_id.is_ghost', '=', True),
                 ('order_id', '=', self.id)])
            # ghost_prd allowed only on draft
            if ghost_prd:
                raise UserError(_(
                    'Ghost product is allowed only on draft Sale Orders.'))

    @api.multi
    def _check_sales_condition(self):
        for so in self:
            if not self.sales_condition:
                raise UserError(_(
                    'You need to attach Sales Condition.'))

    @api.multi
    def _check_validators(self):
        if not (self.engineering_validation_id and
                self.system_validation_id and
                self.process_validation_id):
            raise UserError(_('The Sale Order needs to be reviewed.'))

    def write(self, vals):
        # from ' draft you can switch only to 'final_quote'
        target_state = vals.get('state', 'final_quote')
        if (self.state == 'draft' and
                target_state not in ('cancel', 'final_quote')):
            raise UserError(
                _('A Draft Sale Order can only step to '
                  '"final_quote" or "cancel"'))
        if vals.get('state', 'draft') not in ('cancel', 'draft'):
            self._check_ghost()
            self._check_sales_condition()
            self._check_validators()
        return super(SaleOrder, self).write(vals)

    def action_validate_eng(self):
        self.engineering_validation_id = self.env.context['uid']

    def action_validate_sys(self):
        self.system_validation_id = self.env.context['uid']

    def action_validate_pro(self):
        self.process_validation_id = self.env.context['uid']

    @api.multi
    def action_confirm(self):
        for order in self:
            if order.state == 'draft':
                order.state = 'final_quote'
            else:
                super(SaleOrder, order).action_confirm()
        return True
