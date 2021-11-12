# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mailing_list_to_alert = fields.One2many(
        "res.partner", "company_mailing_list", string="Users to inform course end"
    )
    alerting_delay = fields.Float(string="Alerting delay before end of validity (days)")
