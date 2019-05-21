# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    bso_companies = fields.One2many(
        string='Companies',
        comodel_name='res.company',
        inverse_name='partner_id',
    )
