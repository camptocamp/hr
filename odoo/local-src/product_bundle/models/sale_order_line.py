from openerp import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bundle_wizard_id = fields.Many2one(string='Bundle Wizard',
                                       comodel_name='bundle.wizard',
                                       required=True)

    @api.model
    def bundle_wizard_edit(self):
        return {
            "name": "Edit Bundle",
            "type": "ir.actions.act_window",
            "res_model": "bundle.wizard",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_id": self.bundle_wizard_id.id,
        }
