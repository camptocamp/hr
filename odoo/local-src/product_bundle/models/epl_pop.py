from odoo import models, fields


class EplPop(models.Model):
    _name = 'epl.pop'

    name = fields.Char(
        required=True
    )
    partner_id = fields.Many2one(
        string='Provider',
        comodel_name='res.partner'
    )
    longitude = fields.Float(
        string='Longitude'
    )
    Latitude = fields.Float(
        string='Latitude'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
