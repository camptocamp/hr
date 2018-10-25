# -*- coding: utf-8 -*-


from odoo import models, fields, exceptions


class BackboneSettings(models.Model):
    _name = 'backbone.settings'

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', "Settings already exists")
    ]

    name = fields.Char(
        default='Settings',
        readonly=True
    )
    cympa_url = fields.Char(
        string='CYMPA URL',
        required=True,
    )
    username = fields.Char(
        string='Username',
        required=True,
    )
    password = fields.Char(
        string='Password',
        required=True,
    )
    is_creation_enabled = fields.Boolean(
        string='Enable link creation',
        default=False,
    )
    is_archiving_enabled = fields.Boolean(
        string='Enable link archiving',
        default=False,
    )
    regex_city = fields.Char(
        string='Regex city',
        required=True,
        default='[A-Z]+[A-Z0-9]+',
    )
    regex_pop = fields.Char(
        string='Regex pop',
        required=True,
        default='[A-Z]+[A-Z0-9]+',
    )
    regex_device = fields.Char(
        string='Regex device',
        required=True,
        default='[A-Z]+[A-Z0-9]+',
    )
    regex_pop_code = fields.Char(
        string='Regex pop code',
        required=True,
        default='[A-Z]+[A-Z0-9]+',
    )

    def get(self):
        record = self._get()
        if not record:
            raise exceptions.ValidationError(
                "Settings not found, please check settings menu")
        return record

    def _get(self):
        return self.search([], order='id DESC', limit=1)

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
