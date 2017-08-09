from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bundle_details_id = fields.Many2one(string='Bundle Details',
                                        comodel_name='bundle.details',
                                        required=True)

    @api.model
    def bundle_details_edit(self):
        return {
            "name": "Edit Bundle",
            "type": "ir.actions.act_window",
            "res_model": "bundle.details",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.bundle_details_id.id,
        }
