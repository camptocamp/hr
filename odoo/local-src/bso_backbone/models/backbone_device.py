from odoo import models, fields


class BackboneDevice(models.Model):
    _name = 'backbone.device'
    _order = "name ASC"

    name = fields.Char(
        required=True
    )
    pop_id = fields.Many2one(
        string='POP',
        comodel_name='backbone.pop',
        required=True
    )
    partner_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        domain=[('supplier', '=', True)],
        context={'default_supplier': True}
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
