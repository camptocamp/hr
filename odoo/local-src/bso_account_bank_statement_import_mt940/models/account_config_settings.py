# -*- coding: utf-8 -*-


from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    mt940_files_path = fields.Char(
        string='MT940 Files Path',
        required=True,
    )
    delete_imported_files = fields.Boolean(
        string='Delete Imported Files'
    )

    @api.model
    def get_default_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'mt940_files_path': conf.get_param('mt940.mt940_files_path'),
            'delete_imported_files': conf.get_param(
                'mt940.delete_imported_files'),
        }

    @api.multi
    def set_values(self):
        for rec in self:
            conf = rec.env['ir.config_parameter']
            conf.set_param('mt940.mt940_files_path', rec.mt940_files_path)
            conf.set_param('mt940.delete_imported_files',
                           rec.delete_imported_files)
