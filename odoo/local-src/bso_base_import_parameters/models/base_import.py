from odoo import models, api


class Import(models.TransientModel):
    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, options, dryrun=False):
        return super(Import, self.with_context(dryrun=dryrun)).do(
            fields, options, dryrun=dryrun)
