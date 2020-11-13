from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        return super(StockPicking, self).create(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        return super(StockMove, self).create(vals)
