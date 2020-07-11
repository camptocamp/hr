from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for picking in self:
            if picking.sale_id.is_delivered:
                picking.sale_id.update_subscription()
        return res
