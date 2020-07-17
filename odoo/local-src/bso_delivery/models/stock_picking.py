from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        for picking in self:
            picking.update_delivery_progress_rate()
        return res

    @api.multi
    def update_delivery_progress_rate(self):
        for rec in self:
            delivery_id = rec.sale_id.delivery_project_id
            if delivery_id:
                delivery_id.update_progress_rate_revenue()
