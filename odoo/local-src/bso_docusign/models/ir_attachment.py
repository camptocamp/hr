# -*- coding: utf-8 -*-
import mimetypes

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, values):
        rec = super(IrAttachment, self).create(values)
        rec._update_name()
        return rec

    def _update_name(self):
        if not self.env.context.get('from_docusign'):
            return False
        name = self.name.replace(' ', '')
        extension = mimetypes.guess_extension(self.mimetype)
        name = name[:-len(extension)]
        self.write({
            'datas_fname': '%s_Countersigned%s' % (name, extension),
            'name': '%s_Countersigned%s' % (name, extension)
        })
