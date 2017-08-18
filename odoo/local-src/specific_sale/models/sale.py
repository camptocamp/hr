# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.product_uom.recurring')
    def _compute_has_mrc_product(self):
        for record in self:
            record.has_mrc_product = False
            for sol in record.order_line:
                if sol.product_uom.recurring:
                    record.has_mrc_product = True
                    break

    refusal_reason = fields.Text(track_visibility='onchange')
    has_mrc_product = fields.Boolean(compute='_compute_has_mrc_product')

    @api.model
    def _setup_fields(self, partial):
        super(SaleOrder, self)._setup_fields(partial)
        selection = self._fields['state'].selection
        position = 0
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'draft':
                position = idx
            elif state == 'to_approve':
                exists = True
        if not exists:
            selection.insert(position + 1, (
                'to_approve_tech', _('To Approve (technical)')
            ))
            selection.insert(position + 2, ('refused', _('Refused')))

    @api.multi
    def is_to_approve(self):
        """ Overwrite condition to approve to replace group by
        group_technical_mgmt
        """
        validation_types = ('two_step', 'bso_three_step')
        return (self.company_id.so_double_validation in validation_types and
                self.is_amount_to_approve() and
                not (self.user_has_groups('sales_team.group_sale_manager') or
                     self.user_has_groups('base.group_technical_mgmt')))

    @api.multi
    def is_to_approve_technical(self):
        """ Check if it needs an approval from technical managers
        """
        return (self.company_id.so_double_validation == 'bso_three_step' and
                self.is_amount_to_approve() and
                not self.user_has_groups(
                    'specific_security.group_technical_mgmt'))

    @api.multi
    def action_confirm(self):
        to_approve = self.env['sale.order'].browse()
        to_approve_technical = self.env['sale.order'].browse()
        to_confirm = self.env['sale.order'].browse()
        for order in self:
            if order.is_to_approve():
                to_approve |= order
            elif order.is_to_approve_technical():
                to_approve_technical |= order
            else:
                to_confirm |= order
        to_approve.write({'state': 'to_approve'})
        to_approve_technical.write({'state': 'to_approve_tech'})

        if to_confirm:
            return super(SaleOrder, to_confirm).action_confirm()
        return True

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refused'})

    @api.multi
    def action_draft(self):
        """ Allow set to draft from refused state """
        orders = self.filtered(lambda s: s.state == 'refused')
        orders.write({
            'state': 'draft',
            'procurement_group_id': False,
        })
        orders.mapped('order_line').mapped('procurement_ids').write(
            {'sale_line_id': False})

        todo = self.filtered(lambda s: s.state != 'refused')
        return super(SaleOrder, todo).action_draft()

    @api.multi
    def action_invoicing(self):
        """ Select the wizard to call depending of the products in the order"""
        self.ensure_one()
        if self.has_mrc_product:
            wizard_form = self.env.ref('specific_sale.mrp_invoicing_form')
            first_day_month = datetime.now().replace(day=1)
            model = self.env['wizard.mrp.invoicing'].create(
                    {'ref_date': fields.Datetime.to_string(first_day_month)})
            return {
                'name': 'Select a reference date for invoicing',
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.mrp.invoicing',
                'res_id': model.id,
                'view_id': wizard_form.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'
            }
        else:
            return self.get_create_invoice_action()

    def get_create_invoice_action(self):
        """ Return the response to the wizard to create invoices"""
        action = self.env.ref('sale.action_view_sale_advance_payment_inv')
        model = self.env[action.res_model].create({})
        return {
            'name': action.name,
            'type': action.type,
            'res_model': action.res_model,
            'res_id': model.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    def all_mrc_delivered(self):
        """ Are all MRC product delivered in the sale order"""
        for sol in self.order_line:
            if sol.product_uom.recurring:
                if sol.product_uom_qty > sol.qty_delivered:
                    return False
        return True

    def create_contract(self):
        """ Create the contract only when all mrc products are delivered """
        self.ensure_one()
        if self.all_mrc_delivered():
            super(SaleOrder, self).create_contract()
