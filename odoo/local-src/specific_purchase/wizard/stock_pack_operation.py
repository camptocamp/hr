# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    purchase_lot_ids = fields.Many2many(
        'stock.production.lot',
        string='Purchase Lot',
    )

    @api.multi
    def split_lot(self):
        self.ensure_one()
        res = super(PackOperation, self).split_lot()
        sn = self.picking_id.purchase_id.get_requested_sn()
        if sn:
            res['context']['only_create'] = False
            self[0].purchase_lot_ids = sn
        res['context']['purchase_id'] = self.picking_id.purchase_id.id
        return res

    @api.onchange('product_id')
    def change_product_id(self):
        for item in self:
            po = self.env['purchase.order'].browse(
                self.env.context['purchase_id'])
            item.purchase_lot_ids = po.get_requested_sn()

    @api.onchange('product_id')
    def _compute_purchase_lots(self):
        for item in self:
            po = self.env['purchase.order'].browse(
                self.env.context['purchase_id'])
            item.purchase_lot_ids = po.get_requested_sn()
