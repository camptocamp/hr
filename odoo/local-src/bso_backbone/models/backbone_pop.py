from odoo import models, fields


class BackbonePop(models.Model):
    _name = 'backbone.pop'
    _order = "name ASC"

    name = fields.Char(
        required=True
    )
    partner_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        domain=[('supplier', '=', True)],
        context={'default_supplier': True}
    )
    longitude = fields.Float(
        string='Longitude'
    )
    latitude = fields.Float(
        string='Latitude'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
