from odoo import models, fields


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    perm_chat = fields.Boolean(
        String='Chat Write Access',
        default=True,
    )
    perm_export = fields.Boolean(
        default=False,
    )
