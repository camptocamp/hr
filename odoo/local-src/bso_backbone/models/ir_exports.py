from odoo import models, api, _
from odoo.exceptions import UserError


class IrExports(models.Model):
    _inherit = "ir.exports"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        for _domain in domain:
            field, operator, resource = _domain
            if field == 'resource' and str(resource).startswith('backbone.'):
                group_manager = 'bso_backbone.group_backbone_manager'
                if not self.env.user.has_group(group_manager):
                    raise UserError(_("Export disabled for this resource"))
        return super(IrExports, self).search_read(domain, fields, offset,
                                                  limit, order)
