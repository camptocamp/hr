from odoo import models, fields


class EplDevice(models.Model):
    _name = 'epl.device'

    name = fields.Char(
        required=True
    )
    pop_id = fields.Many2one(
        string='POP',
        comodel_name='epl.pop',
        required=True
    )
    partner_id = fields.Many2one(
        string='Provider',
        comodel_name='res.partner'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
