# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    active = fields.Boolean(
        help="The active field allows you to hide the stage without removing it.",
        default=True,
    )
