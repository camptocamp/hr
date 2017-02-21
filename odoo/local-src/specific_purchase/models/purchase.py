# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        if 'state' in vals and vals['state'] in ('to approve', 'purchase'):
            if self.user_has_groups('purchase.group_purchase_user'):
                super(PurchaseOrder, self).write(vals)
        else:
            super(PurchaseOrder, self).write(vals)
