import json
import hyou
import ast
from odoo import models, fields, api, exceptions


class GoogleSheetSettings(models.Model):
    _name = 'google.sheet.settings'
    sql_constraints = [
        ('unique_name', 'UNIQUE (name)', "Settings already exists")
    ]
    name = fields.Char(
        default='Settings',
        readonly=True
    )
    credentials = fields.Text(string='Google Credentials')

    def get(self):
        record = self._get()
        if not record:
            raise exceptions.ValidationError(
                "Settings not found, please check settings menu")
        return record

    def _get(self):
        return self.search([], order='id DESC', limit=1)

    @api.multi
    def get_json_settings(self):
        credentials = ast.literal_eval(self.credentials)
        return json.dumps(credentials)

    @api.multi
    def get_hyou(self):
        return hyou

    def action_settings(self):
        return {
            "name": "Settings",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "target": "inline",
            "res_model": self._name,
            "res_id": self._get().id,
        }
