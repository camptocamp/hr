# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def is_to_approve(self):
        """ Overwrite condition to approve to replace group by
        group_technical_mgmt
        """
        return (self.company_id.so_double_validation == 'two_step' and
                self.is_amount_to_approve() and
                not self.user_has_groups(
                    'specific_security.group_technical_mgmt'))
