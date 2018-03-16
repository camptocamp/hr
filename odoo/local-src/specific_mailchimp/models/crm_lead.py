# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    mailing_ids = fields.Many2many(
        string="Mailings",
        comodel_name="crm.mailchimp.mailing",
    )
