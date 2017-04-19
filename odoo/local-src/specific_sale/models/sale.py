# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    refusal_reason = fields.Text(track_visibility='onchange')

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
