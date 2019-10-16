# -*- coding: utf-8 -*-


from odoo import models, fields, exceptions


class SalesCommissionSettings(models.Model):
    _name = 'sales.commission.settings'

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', "Settings already exists")
    ]
    name = fields.Char(
        default='Settings',
        readonly=True
    )
    duration_factor_12 = fields.Float(
        string="12 months Term Factor",
        default=1.0,
        required=True,
    )
    duration_factor_24 = fields.Float(
        string="24 months Term Factor",
        default=1.1,
        required=True,
    )
    duration_factor_36 = fields.Float(
        string="36 months Term Factor",
        default=1.2,
        required=True,
    )
    mrr_factor = fields.Float(
        string="MRR Factor",
        default=0.7,
        required=True,
    )
    mrr_factor_fr = fields.Float(
        string="MRR Factor FR",
        default=0.5,
        required=True,
    )
    nrm_factor = fields.Float(
        string="NRR Margin Factor",
        default=0.15,
        required=True,
    )
    renewal_factor_80 = fields.Float(
        string="Renewal Factor (80% to 89%)",
        default=0.1,
        required=True,
    )
    renewal_factor_90 = fields.Float(
        string="Renewal Factor (90% to 99%)",
        default=0.25,
        required=True,
    )
    renewal_factor_100 = fields.Float(
        string="Renewal Factor (>= 100%)",
        default=0.5,
        required=True,
    )
    attainment_factor_0 = fields.Float(
        string="Attainment Factor (0% to 50%)",
        default=0.5,
        required=True,
    )
    attainment_factor_50 = fields.Float(
        string="Attainment Factor (51% to 100%)",
        default=1.0,
        required=True,
    )
    attainment_factor_100 = fields.Float(
        string="Attainment Factor (> 100%)",
        default=1.25,
        required=True,
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
