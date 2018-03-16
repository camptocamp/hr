# -*- coding: utf-8 -*-

from odoo import fields, models


class CrmIndustry(models.Model):
    _name = "crm.industry"

    name = fields.Char(
        required=True,
    )
    subsector_ids = fields.One2many(
        string="Subsectors",
        comodel_name="crm.industry.subsector",
        inverse_name="industry_id",
    )


class CrmIndustrySubsector(models.Model):
    _name = "crm.industry.subsector"

    name = fields.Char(
        required=True,
    )
    industry_id = fields.Many2one(
        string="Industry",
        comodel_name="crm.industry",
        required=True,
    )
