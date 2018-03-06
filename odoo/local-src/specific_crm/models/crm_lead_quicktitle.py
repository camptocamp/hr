# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmLeadQuicktitle(models.Model):
    _name = "crm.lead.quicktitle"

    name = fields.Char(
        string="Name",
        required=True,
    )
