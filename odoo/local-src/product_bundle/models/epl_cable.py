from odoo import models, fields


class EplCable(models.Model):
    _name = 'epl.cable'

    name = fields.Char(
        required=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
