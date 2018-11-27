# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_update_delivery_date(self):
        """Open a wizard to change the delivery date on a done picking."""
        self.ensure_one()
        if self.state == 'done':
            return {
                'name': "Update the delivery date",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.picking.update.delivery_date',
                'view_id': False,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        return True

    @api.multi
    def update_delivery_date(self, delivery_date):
        """Change the `date_done` field of the done pickings in `self` and
        `date` field of all the related done moves with `delivery_date`.

        :param delivery_date: datetime string
        :return: True
        """

        def filter_done(o):
            return o.state == 'done'

        done_pickings = self.filtered(filter_done)
        done_pickings.write({'date_done': delivery_date})
        done_moves = done_pickings.mapped('move_lines').filtered(filter_done)
        done_moves.write({'date': delivery_date})
        return True
