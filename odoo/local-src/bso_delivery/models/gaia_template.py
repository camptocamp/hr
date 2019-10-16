from odoo import models, fields


class GaiaTemplate(models.Model):
    _name = 'gaia.template'

    name = fields.Char(
        string='name'
    )
    desctiption = fields.Char(
        string='description'
    )
