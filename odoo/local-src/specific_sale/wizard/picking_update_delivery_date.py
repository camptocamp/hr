# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class WizardPickingUpdateDeliverydate(models.TransientModel):
    _name = 'wizard.picking.update.delivery_date'
    _description = "Update the delivery date on done pickings."

    picking_id = fields.Many2one(
        'stock.picking', string="Picking", readonly=True,
        default=lambda cls: cls.env.context.get('active_id'))
    delivery_date = fields.Date("New delivery date")

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        self.delivery_date = self.picking_id.date_done

    @api.multi
    def validate(self):
        self.ensure_one()
        self.picking_id.update_delivery_date(self.delivery_date)
        return True
