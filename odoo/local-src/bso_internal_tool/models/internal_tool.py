from odoo import models, fields, api
from odoo.tools import odoo, image_colorize


class InternalTool(models.Model):
    _name = 'internal.tool'

    name = fields.Char(
        string='Name',
        required=True
    )
    icon = fields.Binary(
        string='Icon',
        default=lambda self: self._get_default_icon()
    )
    url = fields.Char(
        string='URL',
        required=True
    )
    description = fields.Text('Description')

    tag_ids = fields.Many2many(
        string='Tags',
        comodel_name='internal.tool.tag'
    )

    @api.model
    def _get_default_icon(self):
        image = image_colorize(
            open(odoo.modules.get_module_resource(
                'bso_internal_tool', 'static/description', 'default.png')
            ).read())

        return image.encode('base64')
