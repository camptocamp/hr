# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('to_approve_tech', 'To Approve (technical)')]
    )

    @api.multi
    def is_to_approve(self):
        """ Overwrite condition to approve to replace group by
        group_technical_mgmt
        """
        validation_types = ('two_step', 'bso_three_step')
        return (self.company_id.so_double_validation in validation_types and
                self.is_amount_to_approve() and
                not (self.user_has_groups('base.group_sale_manager') or
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
        to_approve = self.env['sale.order']
        to_approve_technical = self.env['sale.order']
        to_confirm = self.env['sale.order']
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
