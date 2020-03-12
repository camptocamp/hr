from odoo import models, fields


class InternalToolTag(models.Model):
    _name = 'internal.tool.tag'

    name = fields.Char(
        string='Tag'
    )
    color = fields.Integer('Color Index')
    description = fields.Text(
        string='Description'
    )
    tool_ids = fields.Many2many(
        string='Tools',
        comodel_name='internal.tool',
        inverse_name='tag_id'
    )
