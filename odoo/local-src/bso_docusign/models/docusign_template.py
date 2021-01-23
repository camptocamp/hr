import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class DocusignTemplate(models.Model):
    _inherit = 'docusign.template'

    anchor_ids = fields.One2many(
        string='Anchors',
        comodel_name='docusign.anchor',
        inverse_name='template_id',
    )
    update_state = fields.Boolean(
        string='Update State'
    )

    def get_anchor(self, sign, field):
        return self.anchor_ids.filtered(
            lambda a: a.signature_type == sign and a.field_type == field)
