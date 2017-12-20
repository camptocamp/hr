# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
    state = fields.Selection(
        selection_add=[
            ('to_approve_tech', 'To Approve (technical)'),
            ('refused', 'Refused'),
        ]
    )

    @api.model
    def _setup_fields(self, partial):
        super(SaleOrder, self)._setup_fields(partial)
        selection = self._fields['state'].selection
        idxs = {state[0]: idx for idx, state in enumerate(selection)}
        to_app = selection.pop(idxs['to_approve_tech'])
        # since we've already removed one item here we get back by 1
        refused = selection.pop(idxs['refused'] - 1)
        # place both states right after draft
        selection.insert(idxs['draft'] + 1, to_app)
        selection.insert(idxs['draft'] + 2, refused)

    @api.multi
    def is_to_approve(self):
        """ Overwrite condition to approve to replace group by
        group_technical_mgmt
        """
        self.ensure_one()
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
        to_approve = self.browse()
        to_approve_technical = self.browse()
        to_confirm = self.browse()
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
                if not sol.mrc_fully_delivered():
                    return False
        return True

    def create_contract(self):
        """ Create the contract only when all mrc products are delivered """
        self.ensure_one()
        if self.all_mrc_delivered():
            return super(SaleOrder, self).create_contract()
        else:
            return False

    def _prepare_contract_data(self, payment_token_id=False):
        res = super(SaleOrder, self)._prepare_contract_data(
                payment_token_id=payment_token_id)
        duration = self.order_line.mapped('duration')
        if self.env.context.get('ref_date_mrc_delivery'):
            res['recurring_next_date'] = self.env.context.get(
                    'ref_date_mrc_delivery')[:10]
        if duration:
            res['duration'] = duration[0]
            # date is 'End date' (of course...)
            res['date'] = (fields.Date.from_string(res['date_start']) +
                           relativedelta(months=duration[0]))

        if self.template_id and self.template_id.contract_template:
            contract_tmp = self.template_id.contract_template
        else:
            contract_tmp = self.contract_template
        res.update(automatic_renewal=contract_tmp.automatic_renewal,
                   customer_prior_notice=contract_tmp.customer_prior_notice)
        return res
