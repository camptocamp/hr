# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def write(self, vals):
        if 'state' in vals and vals['state'] in ('to approve', 'purchase'):
            if self.user_has_groups('purchase.group_purchase_user'):
                for line in self.order_line:
                    if line.product_id.is_req_sn_supplier:
                        Lot = self.env['stock.production.lot']
                        values = {
                            'product_id': line.product_id.id,
                        }
                        lot = Lot.create(values)
                        line.req_sn_supplier = lot.name
                super(PurchaseOrder, self).write(vals)
        else:
            super(PurchaseOrder, self).write(vals)

    @api.multi
    def button_approve(self, force=False):
        for order in self:
            for line in order.order_line:
                if not line.account_analytic_id:
                    raise exceptions.UserError(
                        _('An Analytic Account is required for Validation!'))
        return super(PurchaseOrder, self).button_approve(force=force)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    req_sn_supplier = fields.Char(
        string='Requested SN to supplier',
    )
