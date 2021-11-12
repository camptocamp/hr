# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mailing_list_to_alert = fields.Many2one(
        related="company_id.mailing_list_to_alert", readonly=False
    )
    alerting_delay = fields.Float(related="company_id.alerting_delay", readonly=False)
